#!/usr/bin/env python3
"""Render content v3 + visual-plan v1 as a validated editable PPTX."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from design_system import PRESETS, language, normalize_deck, validate_deck
from text_layout import pptx_text
from visual_plan import load_plan, resolved_pages, text_at, validate_plan

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "scripts/fixtures/collaboration-baseline.json"
WORKBENCH = ROOT / "assets/workbench.svg"


def run(*args: str, capture: bool = False) -> str:
    result = subprocess.run(
        ["officecli", *args], check=True, text=True,
        stdout=subprocess.PIPE if capture else subprocess.DEVNULL,
        stderr=subprocess.PIPE if capture else None,
    )
    return result.stdout if capture else ""


def run_json(*args: str) -> dict[str, Any]:
    return json.loads(run(*args, "--json", capture=True))


def text_spec(visual: dict[str, Any], path: str) -> dict[str, Any] | None:
    value = (visual.get("textFlow") or {}).get(path)
    return value if isinstance(value, dict) else None


def text_value(slide: dict[str, Any], visual: dict[str, Any], key: str) -> str:
    return pptx_text(slide.get(key), text_spec(visual, f"/{key}"))


def text_path(slide: dict[str, Any], visual: dict[str, Any], path: str) -> str:
    return pptx_text(text_at(slide, path), text_spec(visual, path))


def explicit_wrap(visual: dict[str, Any], path: str) -> bool | None:
    return False if text_spec(visual, path) else None


def add_shape(
    file: Path, slide: int, text: str, x: str, y: str, w: str, h: str, size: int, color: str,
    theme: dict[str, Any], *, font: str = "body", bold: bool = False, fill: str | None = None,
    line: str | None = None, geometry: str | None = None, wrap: bool | None = None,
) -> None:
    if theme.get("density") == "dense" and size >= 14:
        size = max(10, round(size * .9))
    padded_h = f"{float(h.removesuffix('cm')) + .35:g}cm" if h.endswith("cm") else h
    props = [
        f"text={text}", f"x={x}", f"y={y}", f"w={w}", f"h={padded_h}", f"size={size}", f"color={color}",
        f"font.ea={theme[f'{font}_ea']}", f"font.latin={theme[f'{font}_latin']}", "autoFit=none", "margin=0.08cm",
    ]
    if wrap is not None:
        props.append(f"wrap={'true' if wrap else 'false'}")
    if bold:
        props.append("bold=true")
    if fill:
        props.append(f"fill={fill}")
    if geometry or fill:
        props.append(f"geometry={geometry or ('roundRect' if theme['radius_cm'] else 'rect')}")
    if line:
        props.append(f"line={line}")
    command = ["add", str(file), f"/slide[{slide}]", "--type", "shape"]
    for prop in props:
        command.extend(["--prop", prop])
    run(*command)


def add_note(file: Path, slide: int, value: str) -> None:
    run("add", str(file), f"/slide[{slide}]", "--type", "notes", "--prop", f"text={value}", "--prop", "lang=zh-CN")


def add_header(file: Path, slide: int, theme: dict[str, Any], deck_title: str, number: str) -> None:
    add_shape(file, slide, deck_title, "1cm", ".5cm", "16cm", ".45cm", 9, theme["muted"], theme, font="meta")
    add_shape(file, slide, number, "24cm", ".5cm", "3cm", ".45cm", 9, theme["muted"], theme, font="meta")
    run("add", str(file), f"/slide[{slide}]", "--type", "shape", "--prop", "x=1cm", "--prop", "y=1.35cm", "--prop", "w=2.2cm", "--prop", "h=0.08cm", "--prop", f"fill={theme['accent']}", "--prop", "geometry=rect")


def add_items(file: Path, page: int, slide: dict[str, Any], visual: dict[str, Any], theme: dict[str, Any], presentation: str, *, numbered: bool = False) -> None:
    items = slide["items"]
    count = len(items)
    width, gap = (24 - (count - 1) * .65) / count, .65
    panel = presentation in {"panel-led", "ui-product-led"}
    if presentation == "schematic-led" and numbered:
        add_shape(file, page, "", "1cm", "6.25cm", "24cm", ".04cm", 1, theme["line"], theme, fill=theme["line"], geometry="rect")
    for index, item in enumerate(items):
        x = f"{1 + index * (width + gap):g}cm"
        if panel:
            add_shape(file, page, "", x, "4.5cm", f"{width:g}cm", "7cm", 1, theme["ink"], theme, fill=theme["surface"], line=f"{theme['line']}:{theme['line_width']}")
        elif presentation == "hand-drawn-explainer":
            add_shape(file, page, "", x, "4.65cm", f"{width:g}cm", "5.8cm", 1, theme["ink"], theme, fill=theme["paper"], line=f"{theme['accent']}:1.25pt", geometry="ellipse")
        elif presentation == "editorial-print-led":
            add_shape(file, page, "", x, "4.65cm", f"{width:g}cm", ".04cm", 1, theme["line"], theme, fill=theme["line"], geometry="rect")
        label_key = "label" if item.get("label") is not None else "title"
        label_path = f"/items/{index}/{label_key}"
        label_value = text_path(slide, visual, label_path)
        label = f"{index+1:02d} · {label_value}" if numbered else label_value
        body_path = f"/items/{index}/body"
        add_shape(file, page, label, x, "5.2cm", f"{width:g}cm", "1.2cm", 23, theme["accent"], theme, font="title", bold=True, wrap=explicit_wrap(visual, label_path))
        add_shape(file, page, text_path(slide, visual, body_path), x, "7.1cm", f"{width:g}cm", "2.9cm", 16, theme["ink"], theme, wrap=explicit_wrap(visual, body_path))


def add_picture(file: Path, page: int, asset: dict[str, Any], input_path: Path, x: str, y: str, w: str, h: str) -> None:
    raw = asset.get("path")
    candidates = [(ROOT / str(raw)).resolve(), (input_path.parent / str(raw)).resolve()] if raw else []
    source = next((path for path in candidates if path.is_file()), None)
    if source is None:
        raise FileNotFoundError(f"asset not found: {raw}")
    run("add", str(file), f"/slide[{page}]", "--type", "picture", "--prop", f"src={source}", "--prop", f"x={x}", "--prop", f"y={y}", "--prop", f"width={w}", "--prop", f"height={h}", "--prop", f"alt={asset['alt']}")


def media_layout(count: int, presentation: str) -> list[tuple[str, str, str, str, str]]:
    if count == 1:
        return [("11.5cm", "2.5cm", "14.5cm", "9.8cm", "12.5cm")] if presentation == "photo-led" else [("14cm", "3cm", "12cm", "8cm", "12cm")]
    if count == 2:
        return [("13.2cm", "3.2cm", "6.2cm", "6.8cm", "10.5cm"), ("19.8cm", "3.2cm", "6.2cm", "6.8cm", "10.5cm")]
    if count == 3:
        return [("13cm", "3.6cm", "4.1cm", "5.8cm", "9.9cm"), ("17.45cm", "3.6cm", "4.1cm", "5.8cm", "9.9cm"), ("21.9cm", "3.6cm", "4.1cm", "5.8cm", "9.9cm")]
    raise ValueError("media-evidence supports 1-3 assets")


def add_chart(file: Path, page: int, slide: dict[str, Any], visual: dict[str, Any], theme: dict[str, Any]) -> None:
    data = slide["data"]
    categories_values = [text_path(slide, visual, f"/data/categories/{index}") for index in range(len(data["categories"]))]
    series_values = [{**item, "name": text_path(slide, visual, f"/data/series/{index}/name")} for index, item in enumerate(data["series"])]
    if data["chartType"] == "bar":
        categories_values.reverse()
        for item in series_values:
            item["values"] = list(reversed(item["values"]))
    series = ";".join(f"{item['name']}:" + ",".join(str(value) for value in item["values"]) for item in series_values)
    categories = ",".join(str(value) for value in categories_values)
    props = {
        "chartType": data["chartType"], "categories": categories, "data": series, "x": "10.4cm", "y": "3.5cm", "width": "16.2cm", "height": "9.2cm",
        "colors": ",".join((theme["accent"], theme["ink"], theme["muted"])), "dataLabels": "value", "gridlines": "none", "legend": "bottom",
        "chartareafill": theme["paper"], "chartborder": "none", "axisfont": f"10:{theme['muted']}:{theme['body_latin']}",
    }
    scale = data.get("scale") or {}
    if scale.get("min") is not None:
        props["axismin"] = str(scale["min"])
    if scale.get("max") is not None:
        props["axismax"] = str(scale["max"])
    command = ["add", str(file), f"/slide[{page}]", "--type", "chart"]
    for key, value in props.items():
        command.extend(["--prop", f"{key}={value}"])
    run_json(*command)


def csvish(columns: list[Any], rows: list[list[Any]]) -> str:
    lines: list[str] = []
    for row in [columns, *rows]:
        output = io.StringIO()
        csv.writer(output, lineterminator="").writerow([str(value) for value in row])
        lines.append(output.getvalue())
    return ";".join(lines)


def add_table(file: Path, page: int, slide: dict[str, Any], visual: dict[str, Any], theme: dict[str, Any]) -> None:
    data = slide["data"]
    columns = [text_path(slide, visual, f"/data/columns/{index}") for index in range(len(data["columns"]))]
    rows = [[text_path(slide, visual, f"/data/rows/{row_index}/{column_index}") for column_index in range(len(row))] for row_index, row in enumerate(data["rows"])]
    widths = ["5.2cm"] + [f"{18.8/(len(data['columns'])-1):g}cm"] * (len(data["columns"])-1)
    props = {
        "data": csvish(columns, rows), "x": "1.6cm", "y": "4cm", "width": "24cm", "height": "9.6cm", "colWidths": ",".join(widths),
        "headerFill": theme["accent"], "bodyFill": theme["surface"], "style": "none", "firstRow": "true", "bandedRows": "false",
        "border.horizontal": f"0.5pt solid {theme['line']}", "border.vertical": "none", "border.top": f"1pt solid {theme['ink']}", "border.bottom": f"1pt solid {theme['ink']}",
    }
    command = ["add", str(file), f"/slide[{page}]", "--type", "table"]
    for key, value in props.items():
        command.extend(["--prop", f"{key}={value}"])
    table = run_json(*command)
    path = str(table.get("data") or table.get("message")).split(" at ")[-1]
    for column in range(1, len(data["columns"]) + 1):
        text_flow_path = f"/data/columns/{column - 1}"
        run("set", str(file), f"{path}/tr[1]/tc[{column}]", "--prop", f"text={columns[column - 1]}", "--prop", f"font={theme['meta_latin']}", "--prop", "size=11pt", "--prop", "bold=true", "--prop", "color=FFFFFF", "--prop", "padding=0.16cm", "--prop", f"wrap={'false' if text_spec(visual, text_flow_path) else 'true'}")
    for row in range(2, len(data["rows"]) + 2):
        for column in range(1, len(data["columns"]) + 1):
            text_flow_path = f"/data/rows/{row - 2}/{column - 1}"
            run("set", str(file), f"{path}/tr[{row}]/tc[{column}]", "--prop", f"text={rows[row - 2][column - 1]}", "--prop", f"font={theme['body_latin']}", "--prop", "size=11pt", "--prop", f"color={theme['ink']}", "--prop", f"wrap={'false' if text_spec(visual, text_flow_path) else 'true'}", "--prop", "padding=0.14cm")


def render_slide(file: Path, page: int, slide: dict[str, Any], visual: dict[str, Any], base_language: str, deck_title: str, total: int, input_path: Path) -> None:
    treatment = visual.get("treatment", "default")
    theme = language(base_language, treatment)
    presentation = visual["presentation"]
    add_header(file, page, theme, deck_title, f"{page:02d} / {total:02d}")
    if treatment == "section-emphasis":
        add_shape(file, page, "", ".15cm", "2.1cm", ".3cm", "10.8cm", 1, theme["accent"], theme, fill=theme["accent"], geometry="rect")
    component = slide["component"]
    title = text_value(slide, visual, "title") if slide.get("title") else ""
    if component in {"cover", "section", "closing", "statement"}:
        if presentation == "panel-led":
            add_shape(file, page, "", ".8cm", "2.55cm", "25.5cm", "10.3cm", 1, theme["ink"], theme, fill=theme["surface"], line=f"{theme['line']}:{theme['line_width']}")
        elif presentation == "editorial-print-led" and treatment != "section-emphasis":
            add_shape(file, page, "", ".55cm", "3cm", ".08cm", "9.4cm", 1, theme["accent"], theme, fill=theme["accent"], geometry="rect")
        add_shape(file, page, text_path(slide, visual, "/eyebrow"), "1cm", "3.2cm", "12cm", ".7cm", 14, theme["accent"], theme, font="meta", wrap=explicit_wrap(visual, "/eyebrow"))
        add_shape(file, page, title, "1cm", "4.4cm", "24.5cm", "2.7cm", 44 if component != "statement" else 38, theme["ink"], theme, font="title", bold=True, wrap=explicit_wrap(visual, "/title"))
        subtitle = text_value(slide, visual, "subtitle") if slide.get("subtitle") else text_value(slide, visual, "body")
        if subtitle:
            subtitle_path = "/subtitle" if slide.get("subtitle") else "/body"
            add_shape(file, page, subtitle, "1cm", "8cm", "19cm", "1.5cm", 21, theme["muted"], theme, wrap=explicit_wrap(visual, subtitle_path))
        if slide.get("cta"):
            add_shape(file, page, text_path(slide, visual, "/cta"), "1cm", "11cm", "8cm", ".9cm", 16, theme["ink"], theme, bold=True, fill=theme["accent"], wrap=explicit_wrap(visual, "/cta"))
    elif component in {"collection", "comparison", "sequence"}:
        add_shape(file, page, title, "1cm", "2.2cm", "24cm", "1.3cm", 32, theme["ink"], theme, font="title", bold=True, wrap=explicit_wrap(visual, "/title"))
        add_items(file, page, slide, visual, theme, presentation, numbered=component == "sequence")
    elif component == "relationship":
        add_shape(file, page, title, "1cm", "2.2cm", "24cm", "1.3cm", 32, theme["ink"], theme, font="title", bold=True, wrap=explicit_wrap(visual, "/title"))
        nodes = slide["nodes"]
        width = 10.8
        for index, node in enumerate(nodes):
            column, row = index % 2, index // 2
            x, y = 1 + column * 12.5, 4.5 + row * 2.65
            geometry = "ellipse" if presentation == "hand-drawn-explainer" else None
            line = f"{theme['accent']}:1.25pt" if presentation == "hand-drawn-explainer" else f"{theme['line']}:{theme['line_width']}"
            path = f"/nodes/{index}/label"
            add_shape(file, page, text_path(slide, visual, path), f"{x}cm", f"{y}cm", f"{width}cm", "1.4cm", 18, theme["ink"], theme, font="title", bold=True, fill=theme["surface"], line=line, geometry=geometry, wrap=explicit_wrap(visual, path))
            body_path = f"/nodes/{index}/body"
            if node.get("body"):
                add_shape(file, page, text_path(slide, visual, body_path), f"{x + .35}cm", f"{y + 1.25}cm", f"{width - .7}cm", "1.05cm", 12, theme["muted"], theme, wrap=explicit_wrap(visual, body_path))
        edge_text = "\n".join(f"{text_path(slide, visual, f'/edges/{index}/from')} → {text_path(slide, visual, f'/edges/{index}/to')}  {text_path(slide, visual, f'/edges/{index}/label')}" for index, _edge in enumerate(slide["edges"]))
        add_shape(file, page, edge_text, "14cm", "10.5cm", "12cm", "2.4cm", 12, theme["accent"], theme, font="meta")
    elif component == "media-evidence":
        text_width = "9.5cm" if presentation == "photo-led" else "11.5cm"
        if slide.get("eyebrow"):
            add_shape(file, page, text_path(slide, visual, "/eyebrow"), "1cm", "2.25cm", text_width, ".55cm", 12, theme["accent"], theme, font="meta", wrap=explicit_wrap(visual, "/eyebrow"))
        add_shape(file, page, title, "1cm", "3cm", text_width, "1.6cm", 30, theme["ink"], theme, font="title", bold=True, wrap=explicit_wrap(visual, "/title"))
        add_shape(file, page, text_path(slide, visual, "/body"), "1cm", "5.3cm", text_width, "3cm", 18, theme["muted"], theme, wrap=explicit_wrap(visual, "/body"))
        layout = media_layout(len(slide["assets"]), presentation)
        if presentation == "ui-product-led":
            add_shape(file, page, "", "13.45cm", "2.45cm", "13.1cm", "9.1cm", 1, theme["ink"], theme, fill=theme["surface"], line=f"{theme['line']}:1pt")
        for index, (asset, (picture_x, picture_y, picture_w, picture_h, caption_y)) in enumerate(zip(slide["assets"], layout, strict=True)):
            add_picture(file, page, asset, input_path, picture_x, picture_y, picture_w, picture_h)
            caption_path = f"/assets/{index}/caption" if asset.get("caption") is not None else f"/assets/{index}/label"
            add_shape(file, page, text_path(slide, visual, caption_path), picture_x, caption_y, picture_w, ".5cm", 10, theme["muted"], theme, font="meta", wrap=explicit_wrap(visual, caption_path))
    elif component == "quote":
        run("set", str(file), f"/slide[{page}]", "--prop", f"background={theme['paper']}")
        add_shape(file, page, "“", "1cm", "1.5cm", "3cm", "3cm", 62, theme["accent"], theme, font="title")
        if presentation == "editorial-print-led":
            add_shape(file, page, "", "1.55cm", "4.5cm", ".08cm", "6.3cm", 1, theme["accent"], theme, fill=theme["accent"], geometry="rect")
        add_shape(file, page, text_value(slide, visual, "quote"), "2.4cm", "5cm", "23cm", "4.5cm", 35, theme["ink"], theme, font="title", bold=True, wrap=explicit_wrap(visual, "/quote"))
        add_shape(file, page, text_value(slide, visual, "attribution"), "2.4cm", "11.6cm", "12cm", ".6cm", 12, theme["accent"], theme, font="meta", wrap=explicit_wrap(visual, "/attribution"))
    elif component == "metric":
        data = slide["data"]
        if presentation == "panel-led":
            add_shape(file, page, "", "12.3cm", "3.2cm", "13.7cm", "8.8cm", 1, theme["ink"], theme, fill=theme["surface"], line=f"{theme['line']}:{theme['line_width']}")
        add_shape(file, page, title, "13cm", "3.8cm", "13cm", "1.4cm", 30, theme["ink"], theme, font="title", bold=True, wrap=explicit_wrap(visual, "/title"))
        add_shape(file, page, text_path(slide, visual, "/data/value"), "1cm", "3.2cm", "10.5cm", "5cm", 92, theme["accent"], theme, font="title", bold=True, wrap=explicit_wrap(visual, "/data/value"))
        add_shape(file, page, text_path(slide, visual, "/data/label"), "1cm", "9cm", "10cm", "1cm", 17, theme["ink"], theme, bold=True, wrap=explicit_wrap(visual, "/data/label"))
        add_shape(file, page, text_path(slide, visual, "/data/context"), "13cm", "6cm", "12cm", "3cm", 18, theme["muted"], theme, wrap=explicit_wrap(visual, "/data/context"))
        add_shape(file, page, text_path(slide, visual, "/data/source"), "13cm", "11.8cm", "12cm", ".6cm", 9, theme["muted"], theme, font="meta", wrap=explicit_wrap(visual, "/data/source"))
    elif component == "chart":
        if presentation == "panel-led":
            add_shape(file, page, "", "9.8cm", "3cm", "17.4cm", "10.2cm", 1, theme["ink"], theme, fill=theme["surface"], line=f"{theme['line']}:{theme['line_width']}")
        elif presentation == "editorial-print-led":
            add_shape(file, page, "", "10.4cm", "3.05cm", "16.2cm", ".05cm", 1, theme["ink"], theme, fill=theme["ink"], geometry="rect")
        add_shape(file, page, title, "1cm", "2.4cm", "9.2cm", "2.2cm", 27, theme["ink"], theme, font="title", bold=True, wrap=explicit_wrap(visual, "/title"))
        add_chart(file, page, slide, visual, theme)
        add_shape(file, page, text_path(slide, visual, "/data/source"), "1cm", "12.8cm", "9.2cm", ".7cm", 9, theme["muted"], theme, font="meta", wrap=explicit_wrap(visual, "/data/source"))
    elif component == "table":
        add_shape(file, page, title, "1.6cm", "2.1cm", "24cm", "1.4cm", 30, theme["ink"], theme, font="title", bold=True, wrap=explicit_wrap(visual, "/title"))
        add_table(file, page, slide, visual, theme)
        add_shape(file, page, text_path(slide, visual, "/data/source"), "1.6cm", "14.1cm", "20cm", ".5cm", 8, theme["muted"], theme, font="meta", wrap=explicit_wrap(visual, "/data/source"))
    else:  # pragma: no cover
        raise ValueError(f"unsupported component renderer: {component}")
    if slide.get("footer"):
        add_shape(file, page, text_path(slide, visual, "/footer"), "1cm", "14.4cm", "15cm", ".45cm", 9, theme["muted"], theme, font="meta", wrap=explicit_wrap(visual, "/footer"))
    add_note(file, page, str(slide.get("notes") or "无讲者备注"))


def render_deck(data: dict[str, Any], plan: dict[str, Any], input_path: Path, output: Path, *, allow_candidate: bool = False) -> None:
    normalized = normalize_deck(data)
    pages = resolved_pages(plan, normalized, "pptx", allow_candidate=allow_candidate)
    base_language = plan["language"]["id"]
    run("create", str(output))
    for visual in pages:
        theme = language(base_language, visual.get("treatment", "default"))
        run("add", str(output), "/", "--type", "slide", "--prop", f"background={theme['paper']}")
    total = len(normalized["slides"])
    for page, (slide, visual) in enumerate(zip(normalized["slides"], pages, strict=True), start=1):
        render_slide(output, page, slide, visual, base_language, normalized["deck"]["title"], total, input_path)
    run("save", str(output))
    run("close", str(output))


def close_quietly(path: Path) -> None:
    subprocess.run(["officecli", "close", str(path)], check=False, text=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def validate_candidate(candidate: Path, input_path: Path, preset_name: str | None, plan_path: Path | None, screenshots: Path, *, allow_candidate: bool = False) -> None:
    command = [sys.executable, str(Path(__file__).with_name("validate_pptx.py")), str(candidate), "--fixture", str(input_path), "--screenshots-dir", str(screenshots)]
    if preset_name:
        command.extend(["--preset", preset_name])
    if plan_path:
        command.extend(["--plan", str(plan_path)])
    if allow_candidate:
        command.append("--allow-candidate")
    subprocess.run(command, check=True, text=True)


def publish_pptx(data: dict[str, Any], plan: dict[str, Any], input_path: Path, output: Path, *, preset_name: str | None = None, plan_path: Path | None = None, evidence_dir: Path | None = None, allow_candidate: bool = False) -> Path:
    if output.suffix.lower() != ".pptx":
        raise SystemExit("输出路径必须以 .pptx 结尾")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f".{output.stem}-candidate-", dir=output.parent) as temporary:
        candidate = Path(temporary) / output.name
        screenshots = Path(temporary) / "screenshots"
        try:
            if allow_candidate:
                render_deck(data, plan, input_path, candidate, allow_candidate=True)
                validate_candidate(candidate, input_path, preset_name, plan_path, screenshots, allow_candidate=True)
            else:
                render_deck(data, plan, input_path, candidate)
                validate_candidate(candidate, input_path, preset_name, plan_path, screenshots)
            digest = hashlib.sha256(candidate.read_bytes()).hexdigest()[:12]
            final_evidence = evidence_dir or output.parent / f"{output.stem}-evidence-{digest}"
            if final_evidence.exists():
                index = 2
                base = final_evidence
                while final_evidence.exists():
                    final_evidence = base.with_name(f"{base.name}-{index}")
                    index += 1
            staged_evidence = output.parent / f".{final_evidence.name}-candidate"
            shutil.copytree(screenshots, staged_evidence)
            os.replace(staged_evidence, final_evidence)
            try:
                os.replace(candidate, output)
            except Exception:
                shutil.rmtree(final_evidence, ignore_errors=True)
                raise
            return final_evidence
        finally:
            if candidate.exists():
                close_quietly(candidate)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--preset", choices=PRESETS)
    parser.add_argument("--style", choices=PRESETS, help="deprecated alias for --preset")
    parser.add_argument("--evidence-dir", type=Path)
    parser.add_argument("--prototype-candidate", action="store_true", help="render a candidate-status representative plan; not valid for final manifest")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    errors = validate_deck(data)
    if errors:
        raise SystemExit("invalid mature slide content:\n- " + "\n- ".join(errors))
    preset_name = args.preset or args.style
    try:
        plan = load_plan(args.plan, data, preset_name)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    if args.prototype_candidate and (args.plan is None or (plan.get("prototype") or {}).get("status") != "candidate"):
        raise SystemExit("--prototype-candidate requires an explicit candidate-status visual plan")
    plan_errors = validate_plan(plan, data, "pptx", allow_candidate=args.prototype_candidate)
    if plan_errors:
        raise SystemExit("invalid visual plan:\n- " + "\n- ".join(plan_errors))
    evidence = publish_pptx(data, plan, args.input, args.output, preset_name=preset_name if args.plan is None else None, plan_path=args.plan, evidence_dir=args.evidence_dir, allow_candidate=args.prototype_candidate)
    print(f"PPTX generated: {args.output}; evidence: {evidence}")


if __name__ == "__main__":
    main()
