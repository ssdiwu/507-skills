#!/usr/bin/env python3
"""Validate a generated 507-ppt PPTX with officecli."""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageStat, UnidentifiedImageError

from design_system import DIRECTIONS, direction, visible_strings

ROOT = Path(__file__).resolve().parents[1]


def cli(*args: str) -> str:
    return subprocess.run(["officecli", *args], check=True, text=True, capture_output=True).stdout


def validate_screenshot(path: Path, theme: dict[str, str] | None = None) -> None:
    if not path.is_file() or path.stat().st_size == 0:
        raise SystemExit(f"幻灯片截图缺失或为空：{path}")
    try:
        with Image.open(path) as source:
            image = source.convert("RGB")
    except (OSError, UnidentifiedImageError) as exc:
        raise SystemExit(f"幻灯片截图无法读取：{path}") from exc
    width, height = image.size
    if width < 640 or height < 360 or abs(width / height - 16 / 9) > 0.02:
        raise SystemExit(f"幻灯片截图尺寸异常：{path}（{width}x{height}）")
    if max(ImageStat.Stat(image).stddev) < 5:
        raise SystemExit(f"幻灯片截图视觉内容为空白：{path}")
    if not theme:
        return
    colors = image.getcolors(maxcolors=width * height)
    if colors is None:
        raise SystemExit(f"幻灯片截图颜色扫描失败：{path}")
    total = width * height
    minimum_share = {"paper": 0.005, "ink": 0.005, "accent": 0.0001}
    role_labels = {"paper": "纸面色", "ink": "墨色", "accent": "强调色"}
    for role, share in minimum_share.items():
        target = tuple(bytes.fromhex(theme[role]))
        count = sum(
            amount
            for amount, color in colors
            if max(abs(color[index] - target[index]) for index in range(3)) <= 24
        )
        if count < total * share:
            raise SystemExit(f"幻灯片截图缺少预期{role_labels[role]}：{path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path)
    parser.add_argument("--slides", type=int)
    parser.add_argument("--screenshots-dir", type=Path)
    parser.add_argument("--fixture", type=Path, default=ROOT / "scripts/fixtures/collaboration-baseline.json")
    parser.add_argument("--style", choices=DIRECTIONS)
    args = parser.parse_args()
    if args.file.suffix != ".pptx" or not args.file.is_file():
        raise SystemExit("expected an existing .pptx file")
    fixture = json.loads(args.fixture.read_text(encoding="utf-8"))
    expected_slides = args.slides or len(fixture["slides"])
    if expected_slides != len(fixture["slides"]):
        raise SystemExit("--slides must match the input fixture")
    validation = cli("validate", str(args.file))
    issues = cli("view", str(args.file), "issues")
    missing_alt = cli("query", str(args.file), "picture:no-alt")
    if "Validation passed" not in validation:
        raise SystemExit(validation)
    if "Found 0 issue(s)" not in issues:
        raise SystemExit(issues)
    if missing_alt.strip():
        raise SystemExit(f"pictures without alt text:\n{missing_alt}")
    text = cli("view", str(args.file), "text")
    required = [fixture["deck"]["title"]] + [value for slide in fixture["slides"] for value in visible_strings(slide)]
    missing = [value for value in required if value and value not in text]
    if missing:
        raise SystemExit("fixture text missing from PPTX: " + " | ".join(missing))
    if not cli("query", str(args.file), "shape[font.latin=Menlo]").strip():
        raise SystemExit("missing Menlo metadata font role")
    theme = direction(args.style) if args.style else None
    if theme:
        for font in (theme["title_latin"], theme["meta_latin"]):
            if not cli("query", str(args.file), f"shape[font.latin={font}]").strip():
                raise SystemExit(f"missing direction font role: {font}")
    for number in range(1, expected_slides + 1):
        notes = cli("get", str(args.file), f"/slide[{number}]/notes", "--depth", "1")
        if '""' in notes or not notes.strip():
            raise SystemExit(f"missing notes for slide {number}")
        if args.screenshots_dir:
            args.screenshots_dir.mkdir(parents=True, exist_ok=True)
            screenshot = args.screenshots_dir / f"slide-{number}.png"
            subprocess.run(["officecli", "view", str(args.file), "screenshot", "--start", str(number), "--end", str(number), "-o", str(screenshot)], check=True)
            validate_screenshot(screenshot, theme)
    print(f"PPTX validation passed: {args.file} ({expected_slides} slides)")


if __name__ == "__main__":
    main()
