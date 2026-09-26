#!/usr/bin/env python3
"""Validate a generated 507-ppt PPTX, including native data components."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from pptx_svg import validate_svg_fallbacks

from PIL import Image, ImageStat, UnidentifiedImageError

from design_system import PRESETS, language, normalize_deck, validate_deck, visible_strings
from text_layout import pptx_text
from visual_plan import text_at
from visual_plan import load_plan, resolved_pages, validate_plan

ROOT = Path(__file__).resolve().parents[1]


def cli(*args: str) -> str:
    return subprocess.run(["officecli", *args], check=True, text=True, capture_output=True).stdout


def validate_screenshot(path: Path, theme: dict[str, object] | None = None) -> None:
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
    minimum_share = {"paper": 0.005, "ink": 0.003, "accent": 0.0001}
    role_labels = {"paper": "纸面色", "ink": "墨色", "accent": "强调色"}
    for role, share in minimum_share.items():
        target = tuple(bytes.fromhex(str(theme[role])))
        count = sum(amount for amount, color in colors if max(abs(color[index] - target[index]) for index in range(3)) <= 24)
        if count < total * share:
            raise SystemExit(f"幻灯片截图缺少预期{role_labels[role]}：{path}")


def compact(value: str) -> str:
    return re.sub(r"\s+", "", value)


def descendants(node: object) -> list[dict]:
    found: list[dict] = []
    if isinstance(node, dict):
        found.append(node)
        for value in node.values():
            if isinstance(value, (dict, list)):
                found.extend(descendants(value))
    elif isinstance(node, list):
        for item in node:
            found.extend(descendants(item))
    return found


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path)
    parser.add_argument("--slides", type=int)
    parser.add_argument("--screenshots-dir", type=Path)
    parser.add_argument("--fixture", type=Path, default=ROOT / "scripts/fixtures/collaboration-baseline.json")
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--preset", choices=PRESETS)
    parser.add_argument("--style", choices=PRESETS, help="deprecated alias for --preset")
    parser.add_argument("--allow-candidate", action="store_true", help="validate a prototype candidate plan rather than a final plan")
    args = parser.parse_args()
    if args.file.suffix != ".pptx" or not args.file.is_file():
        raise SystemExit("expected an existing .pptx file")
    try:
        validate_svg_fallbacks(args.file)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    raw = json.loads(args.fixture.read_text(encoding="utf-8"))
    errors = validate_deck(raw)
    if errors:
        raise SystemExit("invalid fixture:\n- " + "\n- ".join(errors))
    fixture = normalize_deck(raw)
    preset_name = args.preset or args.style
    try:
        plan = load_plan(args.plan, raw, preset_name)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    plan_errors = validate_plan(plan, raw, "pptx", allow_candidate=args.allow_candidate)
    if plan_errors:
        raise SystemExit("invalid visual plan:\n- " + "\n- ".join(plan_errors))
    pages = resolved_pages(plan, raw, "pptx", allow_candidate=args.allow_candidate)
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
    document_text = cli("view", str(args.file), "text")
    raw_sections = {
        int(number): body
        for number, body in re.findall(r"=== /slide\[(\d+)\] ===\n(.*?)(?=\n=== /slide\[|\Z)", document_text, flags=re.S)
    }
    sections = {number: compact(body) for number, body in raw_sections.items()}
    if len(sections) != len(fixture["slides"]):
        raise SystemExit("PPTX per-slide text readback is incomplete")
    for number, slide in enumerate(fixture["slides"], start=1):
        values = visible_strings(slide)
        if slide["component"] == "chart":
            data = slide["data"]
            chart_only = {str(item) for item in data.get("categories") or []}
            for series in data.get("series") or []:
                chart_only.add(str(series.get("name")))
                chart_only.update(str(item) for item in series.get("values") or [])
            values = [value for value in values if value not in chart_only]
        values.extend(str(asset["caption"]) for asset in slide.get("assets") or [] if asset.get("caption"))
        missing = [value for value in values if value and compact(value) not in sections[number]]
        if missing:
            raise SystemExit(f"fixture text missing from PPTX slide {number}: " + " | ".join(missing))
        visual = plan["slides"][number - 1]
        for path, spec in (visual.get("textFlow") or {}).items():
            if spec.get("lines"):
                expected_flow = pptx_text(text_at(slide, path), spec)
                if expected_flow not in raw_sections[number]:
                    raise SystemExit(f"PPTX text flow readback mismatch on slide {number}: {path}")
    base_language = plan["language"]["id"]
    base_theme = language(base_language)
    if not cli("query", str(args.file), f"shape[font.latin={base_theme['meta_latin']}]").strip():
        raise SystemExit("missing metadata font role")
    chart_slides = [(number, slide) for number, slide in enumerate(fixture["slides"], start=1) if slide["component"] == "chart"]
    chart_count = len(chart_slides)
    table_count = sum(slide["component"] == "table" for slide in fixture["slides"])
    chart_readback = cli("query", str(args.file), "chart") if chart_count else ""
    if chart_count and len([line for line in chart_readback.splitlines() if line.strip()]) < chart_count:
        raise SystemExit("native chart count is lower than chart components")
    for number, slide in chart_slides:
        data = slide["data"]
        expected = [*(str(item) for item in data["categories"]), *(str(series["name"]) for series in data["series"])]
        if any(value not in chart_readback for value in expected):
            raise SystemExit(f"native chart readback missing categories or series for {slide['id']}")
        tree = json.loads(cli("get", str(args.file), f"/slide[{number}]", "--depth", "2", "--json"))
        chart_nodes = [node for node in descendants(tree) if node.get("type") == "chart"]
        if len(chart_nodes) != 1:
            raise SystemExit(f"slide {number} must contain exactly one native chart")
        chart_format = chart_nodes[0].get("format") or {}
        readback = str(chart_format.get("categories") or "") + " " + " ".join(str(chart_format.get(f"series{index}") or "") for index in range(1, len(data["series"]) + 1))
        if any(value not in readback for value in expected):
            raise SystemExit(f"native chart per-slide readback mismatch for {slide['id']}")
    if table_count and len([line for line in cli("query", str(args.file), "table").splitlines() if line.strip()]) < table_count:
        raise SystemExit("native table count is lower than table components")
    for number, slide in enumerate(fixture["slides"], start=1):
        if slide["component"] != "media-evidence":
            continue
        tree = json.loads(cli("get", str(args.file), f"/slide[{number}]", "--depth", "2", "--json"))
        pictures = [node for node in descendants(tree) if node.get("type") == "picture"]
        expected_alts = [asset["alt"] for asset in slide["assets"]]
        actual_alts = [(node.get("format") or {}).get("alt") for node in pictures]
        if len(pictures) != len(expected_alts) or actual_alts != expected_alts:
            raise SystemExit(f"native picture count or alt readback mismatch for slide {number}")
    for number, visual in enumerate(pages, start=1):
        notes = cli("get", str(args.file), f"/slide[{number}]/notes", "--depth", "1")
        if '""' in notes or not notes.strip():
            raise SystemExit(f"missing notes for slide {number}")
        if args.screenshots_dir:
            args.screenshots_dir.mkdir(parents=True, exist_ok=True)
            screenshot = args.screenshots_dir / f"slide-{number}.png"
            subprocess.run(["officecli", "view", str(args.file), "screenshot", "--start", str(number), "--end", str(number), "-o", str(screenshot)], check=True)
            validate_screenshot(screenshot, language(base_language, visual.get("treatment", "default")))
    print(f"PPTX validation passed: {args.file} ({expected_slides} slides; charts={chart_count}; tables={table_count})")


if __name__ == "__main__":
    main()
