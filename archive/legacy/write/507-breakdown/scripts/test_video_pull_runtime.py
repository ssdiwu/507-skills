#!/usr/bin/env python3
"""Regression test for host-neutral ASR Python selection and dependency reporting."""

from __future__ import annotations

import ast
import os
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).with_name("video_pull.py")


def run_check(*args: str, env: dict[str, str] | None = None) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "check", *args],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr or result.stdout)
    data = ast.literal_eval(result.stdout.strip())
    if not isinstance(data, dict):
        raise AssertionError(f"check output is not a mapping: {data!r}")
    return data


def assert_status(data: dict, expected_python: str) -> None:
    assert data["asr_python"] == expected_python
    assert data["asr_python_exists"] is True
    for key in ("ffmpeg", "ffprobe", "yt_dlp", "tesseract", "faster_whisper", "minimax_key"):
        assert isinstance(data[key], bool), f"{key} must be boolean"


def main() -> int:
    expected = str(Path(sys.executable).absolute())

    explicit_env = os.environ.copy()
    explicit_env["VIDEO_ASR_PYTHON"] = "/definitely/missing/python"
    assert_status(run_check("--asr-python", sys.executable, env=explicit_env), expected)

    environment = os.environ.copy()
    environment["VIDEO_ASR_PYTHON"] = sys.executable
    assert_status(run_check(env=environment), expected)

    default_environment = os.environ.copy()
    default_environment.pop("VIDEO_ASR_PYTHON", None)
    assert_status(run_check(env=default_environment), expected)

    with tempfile.TemporaryDirectory(prefix="asr-python-link-") as tmp:
        linked_python = Path(tmp) / "python"
        linked_python.symlink_to(sys.executable)
        data = run_check("--asr-python", str(linked_python), env=default_environment)
        assert data["asr_python"] == str(linked_python.absolute())
        assert data["asr_python"] != str(linked_python.resolve())

    print("PASS: video_pull selects ASR Python without dereferencing virtual-environment links")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
