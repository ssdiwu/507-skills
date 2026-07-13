#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import math
import shutil
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import render_rednote as renderer


def parse_styles(value: str | None) -> list[str]:
    if not value:
        return list(renderer.STYLE_PRESETS)
    styles = [item.strip() for item in value.split(",") if item.strip()]
    unknown = [item for item in styles if item not in renderer.STYLE_PRESETS]
    if unknown:
        raise SystemExit(f"未知样式：{', '.join(unknown)}")
    return list(dict.fromkeys(styles))


def parse_pages(value: str, page_count: int) -> list[int]:
    try:
        pages = [int(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise SystemExit("--pages 必须是逗号分隔的页码") from exc
    if not pages or any(page < 1 or page > page_count for page in pages):
        raise SystemExit(f"--pages 必须在 1–{page_count}")
    return list(dict.fromkeys(pages))


def label_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]
    for candidate in candidates:
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size=size)
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def render_previews(spec: dict, spec_path: Path, styles: list[str], pages: list[int], chrome: str, timeout: float, temp_dir: Path) -> dict[str, list[Path]]:
    previews: dict[str, list[Path]] = {}
    for style in styles:
        variant = copy.deepcopy(spec)
        variant["stylePreset"] = style
        renderer.validate_spec(variant)
        html_path = temp_dir / f"{style}.html"
        html_path.write_text(renderer.render_html(variant, spec_path), encoding="utf-8")
        previews[style] = []
        for page in pages:
            png_path = temp_dir / f"{style}-{page:02d}.png"
            jpg_path = temp_dir / f"{style}-{page:02d}.jpg"
            renderer.render_png(chrome, html_path.as_uri(), page, png_path, timeout)
            renderer.png_to_jpg(png_path, jpg_path)
            previews[style].append(jpg_path)
        print(f"previewed {style}: pages {pages}")
    return previews


def build_gallery(previews: dict[str, list[Path]], output: Path) -> tuple[int, int]:
    page_thumb = (180, 240)
    page_gap = 8
    label_height = 48
    tile_padding = 12
    tile_width = len(next(iter(previews.values()))) * page_thumb[0] + (len(next(iter(previews.values()))) - 1) * page_gap + tile_padding * 2
    tile_height = page_thumb[1] + label_height + tile_padding * 2
    columns = min(3, len(previews))
    rows = math.ceil(len(previews) / columns)
    gap = 18
    sheet = Image.new("RGB", (columns * tile_width + (columns + 1) * gap, rows * tile_height + (rows + 1) * gap), "#cfcfca")
    draw = ImageDraw.Draw(sheet)
    font = label_font(18)
    for index, (style, files) in enumerate(previews.items()):
        x = gap + (index % columns) * (tile_width + gap)
        y = gap + (index // columns) * (tile_height + gap)
        draw.rounded_rectangle((x, y, x + tile_width, y + tile_height), radius=12, fill="#ffffff", outline="#8f8f88", width=2)
        for page_index, file in enumerate(files):
            with Image.open(file).convert("RGB") as image:
                thumb = ImageOps.fit(image, page_thumb, method=Image.Resampling.LANCZOS)
            px = x + tile_padding + page_index * (page_thumb[0] + page_gap)
            py = y + tile_padding
            sheet.paste(thumb, (px, py))
        label = f"{style} · {renderer.STYLE_LABELS[style]}"
        draw.text((x + tile_padding, y + tile_padding + page_thumb[1] + 10), label, fill="#1a1a1a", font=font)
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, "JPEG", quality=91, optimize=True)
    return sheet.size


def run(args: argparse.Namespace) -> None:
    spec_path = Path(args.spec).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    spec = renderer.load_json(spec_path)
    renderer.validate_spec(spec)
    styles = parse_styles(args.styles)
    pages = parse_pages(args.pages, len(spec["pages"]))
    chrome = renderer.find_chrome(args.chrome)
    temp_root = Path(tempfile.mkdtemp(prefix="rednote-style-gallery-"))
    try:
        previews = render_previews(spec, spec_path, styles, pages, chrome, args.timeout, temp_root)
        size = build_gallery(previews, output_dir / "style-gallery.jpg")
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)
    manifest = {
        "sourceSpec": str(spec_path),
        "sourceSpecSha256": renderer.sha256(spec_path),
        "styles": [{"id": style, "name": renderer.STYLE_LABELS[style]} for style in styles],
        "previewPages": pages,
        "gallery": "style-gallery.jpg",
        "gallerySize": list(size),
    }
    (output_dir / "style-gallery.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"outputDir": str(output_dir), "styleCount": len(styles), "gallerySize": size}, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="小红书图文样式预览脚本")
    parser.add_argument("--spec", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--styles", help="逗号分隔的样式 ID；默认全部")
    parser.add_argument("--pages", default="1,2", help="每种样式预览哪些页面，默认 1,2")
    parser.add_argument("--chrome")
    parser.add_argument("--timeout", type=float, default=25.0)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
