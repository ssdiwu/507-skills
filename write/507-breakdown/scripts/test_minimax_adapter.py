#!/usr/bin/env python3
"""Strict MiniMax-M3 adapter smoke test.

Default mode requires MiniMax_API_KEY and performs a real upload +
/anthropic/v1/messages call. If no --video is given it deterministically
creates an 8-second black MP4 with ffmpeg. It never silently skips.

Use --no-key to test the independent no-key failure contract.
Use --evidence-dir to keep the real output JSON/manifest for review.
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys, tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


def make_synthetic_video(path: Path) -> None:
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=640x360:d=8", "-f", "lavfi", "-i", "sine=frequency=440:duration=8", "-c:v", "libx264", "-c:a", "aac", "-shortest", str(path)], check=True, capture_output=True)


def setup_workspace(video: Path, root: Path) -> Path:
    ws = root / "workspace"; (ws / "raw").mkdir(parents=True); (ws / "analysis").mkdir()
    sys.path.insert(0, str(SCRIPTS))
    from video_contract import VideoManifest, video_hash
    m = VideoManifest(ws); m.data["videoPath"] = str(video); m.data["videoHash"] = video_hash(video); m.flush()
    return ws


def assert_result(ws: Path) -> None:
    data = json.loads((ws / "analysis" / "video_understanding_minimax.json").read_text(encoding="utf-8"))
    if not isinstance(data.get("videoThesis"), str) or not data["videoThesis"].strip(): raise RuntimeError("videoThesis missing")
    if not isinstance(data.get("videoTypeHint"), str) or not data["videoTypeHint"].strip(): raise RuntimeError("videoTypeHint missing")
    required = {"id", "meaning", "spokenAnchors", "visualAnchors", "referencePosition", "referenceTimeHint", "status"}
    for i, unit in enumerate(data.get("semanticUnits", [])):
        if required - set(unit): raise RuntimeError(f"unit[{i}] missing {required-set(unit)}")
        if not isinstance(unit["id"], str) or not isinstance(unit["meaning"], str): raise RuntimeError(f"unit[{i}] id/meaning type")
        if not all(isinstance(x, str) for x in unit["spokenAnchors"] + unit["visualAnchors"]): raise RuntimeError(f"unit[{i}] anchor type")
        if not isinstance(unit["referencePosition"], str) or not isinstance(unit["referenceTimeHint"], str): raise RuntimeError(f"unit[{i}] reference type")
        if unit["status"] != "unlocalized": raise RuntimeError(f"unit[{i}] not unlocalized")
    if not data.get("semanticUnits"): raise RuntimeError("empty semanticUnits")
    manifest = json.loads((ws / "raw" / "video_manifest.json").read_text(encoding="utf-8"))
    if manifest.get("status") != "video_understood": raise RuntimeError(f"manifest={manifest.get('status')}")
    print(f"PASS: real M3 call, {len(data['semanticUnits'])} units, hash={manifest['videoHash']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="严格 MiniMax-M3 真实 smoke test")
    parser.add_argument("--video")
    parser.add_argument("--evidence-dir")
    parser.add_argument("--no-key", action="store_true", help="仅测试无 key 的 semantic_failed 合约")
    args = parser.parse_args()
    root = Path(args.evidence_dir).resolve() if args.evidence_dir else Path(tempfile.mkdtemp(prefix="video-breakdown-m3-"))
    root.mkdir(parents=True, exist_ok=True)

    if args.no_key:
        old = os.environ.pop("MiniMax_API_KEY", None)
        ws = root / "workspace"; (ws / "raw").mkdir(parents=True); (ws / "analysis").mkdir()
        (ws / "raw" / "video_manifest.json").write_text(json.dumps({"status": "running", "videoPath": "/nonexistent.mp4"}))
        result = subprocess.run([sys.executable, str(SCRIPTS / "video_understand_minimax.py"), "--workspace", str(ws)], capture_output=True, text=True)
        if old is not None: os.environ["MiniMax_API_KEY"] = old
        manifest = json.loads((ws / "raw" / "video_manifest.json").read_text())
        if result.returncode == 0 or manifest.get("status") != "video_semantic_failed": raise RuntimeError("no-key contract failed")
        print("PASS: no-key contract")
        return 0

    if not os.getenv("MiniMax_API_KEY"):
        raise SystemExit("MiniMax_API_KEY is required for real smoke test; use --no-key for failure-contract test")
    video = Path(args.video).resolve() if args.video else root / "video_synthetic_8s.mp4"
    if not args.video: make_synthetic_video(video)
    if not video.exists(): raise SystemExit(f"test video not found: {video}")
    ws = setup_workspace(video, root)
    result = subprocess.run([sys.executable, str(SCRIPS := SCRIPTS / "video_understand_minimax.py"), "--workspace", str(ws), "--fps", "1"], capture_output=True, text=True)
    if result.returncode != 0: raise SystemExit(result.stderr[-1000:])
    assert_result(ws)
    print(f"evidence_dir={root}")
    return 0


if __name__ == "__main__": raise SystemExit(main())
