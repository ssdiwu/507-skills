#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def detect_language(requested: str | None) -> str:
    if requested:
        return requested
    result = subprocess.run(['tesseract', '--list-langs'], check=True, capture_output=True, text=True)
    available = set(line.strip() for line in result.stdout.splitlines() if line.strip() and not line.startswith('List'))
    if {'chi_sim', 'eng'}.issubset(available):
        return 'chi_sim+eng'
    if 'eng' in available:
        return 'eng'
    return 'osd'


def main() -> int:
    parser = argparse.ArgumentParser(description="Tesseract OCR helper")
    parser.add_argument("image_path")
    parser.add_argument("output_path")
    parser.add_argument("--lang")
    args = parser.parse_args()

    output_path = Path(args.output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "tesseract",
        args.image_path,
        str(output_path.with_suffix("")),
        "-l",
        detect_language(args.lang),
        "--psm",
        "6",
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    txt_path = output_path.with_suffix(".txt")
    if txt_path != output_path:
        txt_path.rename(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
