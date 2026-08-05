#!/usr/bin/env python3
"""Regression tests for transactional --force workspace replacement."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import video_pull
from video_contract import STATUS_ANALYSIS_READY, STATUS_COMPLETED, STATUS_FAILED, VideoManifest


class VideoPullForceTests(unittest.TestCase):
    def run_main(self, root: Path, *extra: str) -> int:
        argv = [
            "video_pull.py",
            "run",
            "--video",
            "input.mp4",
            "--output-dir",
            str(root),
            "--title-hint",
            "sample",
            *extra,
        ]
        with patch.object(sys, "argv", argv):
            return video_pull.main()

    def existing_workspace(self, root: Path, status: str = "running") -> Path:
        workspace = root / "sample"
        marker = workspace / "old-marker.txt"
        marker.parent.mkdir(parents=True)
        marker.write_text("old", encoding="utf-8")
        manifest = VideoManifest(workspace)
        manifest.data["status"] = status
        manifest.flush()
        return workspace

    def test_candidate_failure_preserves_existing_workspace(self) -> None:
        with tempfile.TemporaryDirectory(prefix="video-pull-force-") as tmp:
            root = Path(tmp)
            workspace = self.existing_workspace(root)
            with patch.object(video_pull, "acquire", side_effect=RuntimeError("synthetic candidate failure")):
                with self.assertRaisesRegex(RuntimeError, "synthetic candidate failure"):
                    self.run_main(root, "--force")
            self.assertEqual((workspace / "old-marker.txt").read_text(encoding="utf-8"), "old")

    def test_successful_candidate_replaces_workspace_with_portable_paths(self) -> None:
        with tempfile.TemporaryDirectory(prefix="video-pull-force-") as tmp:
            root = Path(tmp)
            workspace = self.existing_workspace(root)

            def fake_acquire(_video: str, manifest: VideoManifest) -> Path:
                path = manifest.workspace / "raw" / "video_source" / "input.mp4"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"candidate")
                return path

            def fake_call(name: str, candidate: Path, *_extra: str) -> None:
                if name == "video_prepare_analysis.py":
                    VideoManifest.load(candidate).set_status(STATUS_ANALYSIS_READY)

            with (
                patch.object(video_pull, "acquire", side_effect=fake_acquire),
                patch.object(video_pull, "video_hash", return_value="hash"),
                patch.object(video_pull, "asr"),
                patch.object(video_pull, "scene_cut"),
                patch.object(video_pull, "call", side_effect=fake_call),
            ):
                self.assertEqual(self.run_main(root, "--force", "--force-local-fallback"), 0)

            self.assertFalse((workspace / "old-marker.txt").exists())
            manifest = json.loads((workspace / "raw" / "video_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["status"], STATUS_ANALYSIS_READY)
            self.assertEqual(manifest["videoPath"], "raw/video_source/input.mp4")
            self.assertTrue((workspace / manifest["videoPath"]).is_file())
            self.assertEqual(list(root.glob(".video-pull-candidate-*")), [])

    def test_completed_workspace_is_not_replaced_by_analysis_candidate(self) -> None:
        with tempfile.TemporaryDirectory(prefix="video-pull-force-") as tmp:
            root = Path(tmp)
            workspace = self.existing_workspace(root, STATUS_COMPLETED)
            with patch.object(video_pull, "acquire") as acquire:
                with self.assertRaisesRegex(SystemExit, "video_completed"):
                    self.run_main(root, "--force")
            acquire.assert_not_called()
            self.assertEqual((workspace / "old-marker.txt").read_text(encoding="utf-8"), "old")

    def test_candidate_below_ready_status_preserves_existing_workspace(self) -> None:
        with tempfile.TemporaryDirectory(prefix="video-pull-force-") as tmp:
            root = Path(tmp)
            workspace = self.existing_workspace(root)

            def fake_acquire(_video: str, manifest: VideoManifest) -> Path:
                path = manifest.workspace / "raw" / "video_source" / "input.mp4"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"candidate")
                return path

            with (
                patch.object(video_pull, "acquire", side_effect=fake_acquire),
                patch.object(video_pull, "video_hash", return_value="hash"),
                patch.object(video_pull, "asr"),
                patch.object(video_pull, "scene_cut"),
                patch.object(video_pull, "call"),
            ):
                with self.assertRaisesRegex(RuntimeError, STATUS_ANALYSIS_READY):
                    self.run_main(root, "--force", "--force-local-fallback")

            self.assertEqual((workspace / "old-marker.txt").read_text(encoding="utf-8"), "old")
            candidates = list(root.glob(".video-pull-candidate-*/sample"))
            self.assertEqual(len(candidates), 1)
            failed = VideoManifest.load(candidates[0]).data
            self.assertEqual(failed["status"], STATUS_FAILED)
            self.assertIn(STATUS_ANALYSIS_READY, failed["notes"][-1])

    def test_publish_failure_restores_existing_workspace(self) -> None:
        with tempfile.TemporaryDirectory(prefix="video-pull-force-") as tmp:
            root = Path(tmp)
            workspace = self.existing_workspace(root)
            candidate = root / "candidate"
            candidate.mkdir()
            (candidate / "new-marker.txt").write_text("new", encoding="utf-8")
            original_replace = video_pull.os.replace

            def fail_candidate_install(source, target):
                if Path(source) == candidate and Path(target) == workspace:
                    raise OSError("synthetic publish failure")
                return original_replace(source, target)

            with patch.object(video_pull.os, "replace", side_effect=fail_candidate_install):
                with self.assertRaisesRegex(OSError, "synthetic publish failure"):
                    video_pull.promote_workspace(candidate, workspace)

            self.assertEqual((workspace / "old-marker.txt").read_text(encoding="utf-8"), "old")
            self.assertTrue(candidate.is_dir())


if __name__ == "__main__":
    unittest.main()
