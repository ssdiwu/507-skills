#!/usr/bin/env python3
"""Render a mature slide-content package as an editable PPTX through officecli."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from design_system import DIRECTIONS, direction, validate_deck

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "scripts/fixtures/collaboration-baseline.json"
WORKBENCH = ROOT / "assets/workbench.svg"


def run(*args: str) -> None:
    subprocess.run(["officecli", *args], check=True, text=True, stdout=subprocess.DEVNULL)


def add_shape(file: Path, slide: int, text: str, x: str, y: str, w: str, h: str, size: int, color: str, theme: dict[str, str], *, font: str = "body", bold: bool = False, fill: str | None = None) -> None:
    padded_h = f"{float(h.removesuffix('cm')) + .7:g}cm" if h.endswith("cm") else h
    props = [f"text={text}", f"x={x}", f"y={y}", f"w={w}", f"h={padded_h}", f"size={size}", f"color={color}", f"font.ea={theme[f'{font}_ea']}", f"font.latin={theme[f'{font}_latin']}"]
    if bold:
        props.append("bold=true")
    if fill:
        props.append(f"fill={fill}")
    command = ["add", str(file), f"/slide[{slide}]", "--type", "shape"]
    for prop in props:
        command.extend(["--prop", prop])
    run(*command)


def add_note(file: Path, slide: int, value: str) -> None:
    run("add", str(file), f"/slide[{slide}]", "--type", "notes", "--prop", f"text={value}", "--prop", "lang=zh-CN")


def header(file: Path, slide: int, theme: dict[str, str], deck_title: str, number: str) -> None:
    add_shape(file, slide, deck_title, "1cm", ".5cm", "16cm", ".45cm", 9, theme["ink"], theme, font="meta")
    add_shape(file, slide, number, "24.2cm", ".5cm", "3.2cm", ".45cm", 9, theme["ink"], theme, font="meta")


def add_items(file: Path, page: int, items: list[dict], theme: dict[str, str], *, fill: str | None = None) -> None:
    count = len(items)
    width, gap = (24 - (count - 1) * .8) / count, .8
    for index, item in enumerate(items):
        x = f"{1 + index * (width + gap):g}cm"
        add_shape(file, page, str(item.get("label") or item.get("title") or ""), x, "5.2cm", f"{width:g}cm", "1.2cm", 26, theme["accent"], theme, font="title", bold=True, fill=fill)
        add_shape(file, page, str(item.get("body") or ""), x, "7.3cm", f"{width:g}cm", "2.6cm", 17, theme["ink"], theme, fill=fill)


def render_slide(file: Path, page: int, slide: dict, theme: dict[str, str], deck_title: str, total: int) -> None:
    header(file, page, theme, deck_title, f"{page:02d} / {total:02d}")
    kind = slide["kind"]
    if kind == "cover":
        add_shape(file, page, slide.get("eyebrow", ""), "1cm", "4cm", "13cm", ".8cm", 17, theme["accent"], theme, font="meta")
        add_shape(file, page, slide["title"], "1cm", "5.2cm", "23cm", "2cm", 48, theme["ink"], theme, font="title", bold=True)
        add_shape(file, page, slide["subtitle"], "1cm", "8cm", "18cm", ".9cm", 23, theme["ink"], theme)
        add_shape(file, page, slide.get("footer", ""), "1cm", "14.2cm", "12cm", ".45cm", 10, theme["ink"], theme, font="meta")
    elif kind == "section":
        add_shape(file, page, slide.get("eyebrow", ""), "1cm", "4cm", "10cm", ".8cm", 17, theme["accent"], theme, font="meta")
        add_shape(file, page, slide["title"], "1cm", "5.2cm", "23cm", "2cm", 48, theme["ink"], theme, font="title", bold=True)
        add_shape(file, page, slide["subtitle"], "1cm", "8.1cm", "18cm", ".9cm", 23, theme["ink"], theme)
    elif kind == "image-text":
        add_shape(file, page, slide.get("eyebrow", ""), "1cm", "3cm", "10cm", ".6cm", 15, theme["accent"], theme, font="meta")
        add_shape(file, page, slide["title"], "1cm", "4cm", "12cm", "1.3cm", 34, theme["ink"], theme, font="title", bold=True)
        add_shape(file, page, slide["body"], "1cm", "6cm", "12cm", "2.4cm", 20, theme["ink"], theme)
        run("add", str(file), f"/slide[{page}]", "--type", "picture", "--prop", f"src={WORKBENCH}", "--prop", "x=15.2cm", "--prop", "y=4cm", "--prop", "width=11.5cm", "--prop", "height=6cm", "--prop", f"alt={slide['asset']['alt']}")
        add_shape(file, page, slide.get("caption", ""), "15.2cm", "10.3cm", "11.5cm", ".45cm", 10, theme["ink"], theme, font="meta")
    elif kind in {"three-part", "process", "comparison"}:
        add_shape(file, page, slide["title"], "1cm", "2.5cm", "24cm", "1.3cm", 34, theme["ink"], theme, font="title", bold=True)
        add_items(file, page, slide["items"], theme, fill=theme["paper"] if kind == "comparison" else None)
        if slide.get("footer"):
            add_shape(file, page, slide["footer"], "1cm", "13.3cm", "24cm", ".7cm", 18, theme["ink"], theme, font="title")
    elif kind == "metric":
        add_shape(file, page, slide["metric"], "1cm", "3cm", "11cm", "4cm", 96, theme["accent"], theme, font="title", bold=True)
        add_shape(file, page, slide["title"], "13cm", "4cm", "13cm", "1.3cm", 34, theme["ink"], theme, font="title", bold=True)
        add_shape(file, page, slide["body"], "13cm", "6cm", "11cm", "2.4cm", 20, theme["ink"], theme)
    else:
        run("set", str(file), f"/slide[{page}]", "--prop", f"background={theme['ink']}")
        add_shape(file, page, "“", "1cm", "1cm", "3cm", "3cm", 80, theme["accent"], theme, font="title")
        add_shape(file, page, slide["quote"], "3cm", "6cm", "22cm", "3.5cm", 38, theme["paper"], theme, font="title", bold=True)
        add_shape(file, page, slide["attribution"], "3cm", "12cm", "12cm", ".5cm", 12, theme["accent"], theme)
    add_note(file, page, slide.get("notes") or "无讲者备注")


def render_deck(data: dict, theme: dict[str, str], output: Path) -> None:
    run("create", str(output))
    for _ in data["slides"]:
        run("add", str(output), "/", "--type", "slide", "--prop", f"background={theme['paper']}")
    total = len(data["slides"])
    for page, slide in enumerate(data["slides"], start=1):
        render_slide(output, page, slide, theme, data["deck"]["title"], total)
    run("save", str(output))
    run("close", str(output))


def close_quietly(path: Path) -> None:
    subprocess.run(
        ["officecli", "close", str(path)],
        check=False,
        text=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def validate_candidate(candidate: Path, input_path: Path, style: str) -> None:
    screenshots = candidate.parent / "screenshots"
    subprocess.run(
        [
            sys.executable,
            str(Path(__file__).with_name("validate_pptx.py")),
            str(candidate),
            "--fixture",
            str(input_path),
            "--style",
            style,
            "--screenshots-dir",
            str(screenshots),
        ],
        check=True,
        text=True,
    )


def publish_pptx(data: dict, input_path: Path, style: str, output: Path) -> None:
    if output.suffix.lower() != ".pptx":
        raise SystemExit("输出路径必须以 .pptx 结尾")
    output.parent.mkdir(parents=True, exist_ok=True)
    theme = direction(style)
    with tempfile.TemporaryDirectory(prefix=f".{output.stem}-candidate-", dir=output.parent) as temp:
        candidate = Path(temp) / output.name
        try:
            render_deck(data, theme, candidate)
            validate_candidate(candidate, input_path, style)
            os.replace(candidate, output)
        finally:
            if candidate.exists():
                close_quietly(candidate)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--style", choices=DIRECTIONS, required=True)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    errors = validate_deck(data)
    if errors:
        raise SystemExit("invalid mature slide content:\n- " + "\n- ".join(errors))
    if not WORKBENCH.is_file():
        raise SystemExit("local workbench asset missing")
    publish_pptx(data, args.input, args.style, args.output)


if __name__ == "__main__":
    main()
