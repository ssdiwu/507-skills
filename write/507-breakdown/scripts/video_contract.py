#!/usr/bin/env python3
"""Shared workspace contract for the 507 video breakdown pipeline."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VIDEO_META = "video_meta.md"
VIDEO_TRANSCRIPT = "video_transcript.md"
VIDEO_BREAKDOWN_MD = "video_breakdown.md"
VIDEO_BREAKDOWN_JSON = "video_breakdown.json"
VIDEO_MANIFEST = "video_manifest.json"
VIDEO_WINDOWS = "video_windows.jsonl"

RAW_DIR = "raw"
ANALYSIS_DIR = "analysis"
RAW_VIDEO_DIR = "video_source"
RAW_LOCATOR_DIR = "video_frames_locator"
RAW_SCENECUT_DIR = "video_frames_scene_cut"
RAW_ADAPTIVE_DIR = "video_frames_adaptive"
RAW_OCR_DIR = "video_ocr"
RAW_ASR_DIR = "video_asr"
RAW_CONTACT_DIR = "video_contact_sheets"

STATUS_ACQUIRED = "video_acquired"
STATUS_UNDERSTOOD = "video_understood"
STATUS_LOCALIZED = "video_localized"
STATUS_VISUALLY_VERIFIED = "video_visually_verified"
STATUS_ANALYSIS_READY = "video_analysis_ready"
STATUS_COMPLETED = "video_completed"
STATUS_SEMANTIC_FAILED = "video_semantic_failed"
STATUS_FAILED = "video_failed"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def video_hash(path: Path) -> str:
    """Full content hash: cache identity for a durable archived source video."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


class VideoManifest:
    def __init__(self, workspace: Path, data: dict[str, Any] | None = None):
        self.workspace = workspace
        self.raw_dir = workspace / RAW_DIR
        self.path = self.raw_dir / VIDEO_MANIFEST
        self.data = data or {
            "status": "running",
            "analysisMode": "minimax_required",
            "semanticSource": "minimax_m3",
            "limitations": [],
            "videoInput": None,
            "videoPath": None,
            "videoHash": None,
            "steps": {},
            "notes": [],
            "updatedAt": utc_now(),
        }

    @classmethod
    def load(cls, workspace: Path) -> "VideoManifest":
        path = workspace / RAW_DIR / VIDEO_MANIFEST
        if not path.exists():
            raise SystemExit(f"缺少工作区 manifest：{path}")
        return cls(workspace, json.loads(path.read_text(encoding="utf-8")))

    def flush(self) -> None:
        ensure_dir(self.raw_dir)
        self.data["updatedAt"] = utc_now()
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")

    def set_status(self, status: str) -> None:
        self.data["status"] = status
        self.flush()

    def set_mode(self, mode: str, semantic_source: str, limitations: list[str] | None = None) -> None:
        self.data["analysisMode"] = mode
        self.data["semanticSource"] = semantic_source
        self.data["limitations"] = limitations or []
        self.flush()

    def step(self, name: str, status: str, detail: str, output: str | None = None, **extra: Any) -> None:
        result: dict[str, Any] = {"status": status, "detail": detail, "at": utc_now()}
        if output:
            result["output"] = output
        result.update(extra)
        self.data.setdefault("steps", {})[name] = result
        self.flush()

    def note(self, message: str) -> None:
        self.data.setdefault("notes", []).append(message)
        self.flush()


def require_completed_manifest(workspace: Path) -> VideoManifest:
    manifest = VideoManifest.load(workspace)
    if manifest.data.get("status") != STATUS_COMPLETED:
        raise SystemExit(
            f"拉片包尚未完成：status={manifest.data.get('status')!r}；"
            f"请先完成并运行 video_validate_breakdown.py --workspace {workspace}"
        )
    return manifest
