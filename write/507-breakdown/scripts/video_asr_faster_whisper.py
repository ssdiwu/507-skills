#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from faster_whisper import WhisperModel


def format_timestamp(seconds: float) -> str:
    total = int(seconds)
    minutes, secs = divmod(total, 60)
    return f"{minutes:02d}:{secs:02d}"


def main() -> int:
    parser = argparse.ArgumentParser(description="faster-whisper transcript helper")
    parser.add_argument("audio_path")
    parser.add_argument("output_path")
    parser.add_argument("--language", default="auto")
    parser.add_argument("--model", default="small")
    args = parser.parse_args()

    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    language = None if args.language == "auto" else args.language
    segments, info = model.transcribe(args.audio_path, language=language)

    lines = []
    for segment in segments:
        lines.append(
            f"[{format_timestamp(segment.start)}-{format_timestamp(segment.end)}] {segment.text.strip()}"
        )

    output = Path(args.output_path)
    output.write_text("\n".join(lines), encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
