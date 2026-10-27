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


def parse_themes(value: str | None) -> list[str]:
    if not value:
        return list(renderer.THEME_PRESETS)
    themes = [item.strip() for item in value.split(",") if item.strip()]
    unknown = [item for item in themes if item not in renderer.THEME_PRESETS]
    if unknown:
        raise SystemExit(f"未知主题：{', '.join(unknown)}")
    return list(dict.fromkeys(themes))


def parse_pages(value: str, page_count: int) -> list[int]:
    try:
        pages = [int(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise SystemExit("--pages 必须是逗号分隔的页码") from exc
    if not pages or any(page < 1 or page > page_count for page in pages):
        raise SystemExit(f"--pages 必须在 1–{page_count}")
    return list(dict.fromkeys(pages))


def label_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in ("/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/STHeiti Medium.ttc"):
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size=size)
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def render_previews(spec: dict, spec_path: Path, themes: list[str], pages: list[int], chrome: str, timeout: float, temp_dir: Path) -> dict[str, list[Path]]:
    previews: dict[str, list[Path]] = {}
    for theme in themes:
        variant = copy.deepcopy(spec)
        variant["themePreset"] = theme
        variant["visualSystem"] = renderer.THEME_PRESETS[theme]["system"]
        renderer.validate_spec(variant)
        poster_dir = temp_dir / f"{theme}-posters"
        poster_dir.mkdir(parents=True, exist_ok=True)
        prepared, _ = renderer.prepare_motion_posters(variant, spec_path, poster_dir)
        html_path = temp_dir / f"{theme}.html"
        html_path.write_text(renderer.render_html(prepared, spec_path), encoding="utf-8")
        audit = renderer.inspect_layout(chrome, html_path.as_uri(), timeout)
        if audit.failures():
            raise SystemExit(f"{theme} 预览布局失败：{'；'.join(audit.failures())}")
        previews[theme] = []
        for page in pages:
            png_path = temp_dir / f"{theme}-{page:02d}.png"
            jpg_path = temp_dir / f"{theme}-{page:02d}.jpg"
            canvas = renderer.page_canvas(variant, page)
            renderer.render_png(chrome, html_path.as_uri(), f"rednote-{page:02d}", png_path, canvas["css"], timeout)
            renderer.png_to_jpg(png_path, jpg_path, canvas["output"])
            previews[theme].append(jpg_path)
        print(f"previewed {theme}: pages {pages}")
    return previews


def build_gallery(previews: dict[str, list[Path]], output: Path) -> tuple[int, int]:
    page_thumb = (180, 300)
    page_gap = 8
    label_height = 56
    tile_padding = 12
    preview_count = len(next(iter(previews.values())))
    tile_width = preview_count * page_thumb[0] + (preview_count - 1) * page_gap + tile_padding * 2
    tile_height = page_thumb[1] + label_height + tile_padding * 2
    columns = min(3, len(previews))
    rows = math.ceil(len(previews) / columns)
    gap = 18
    sheet = Image.new("RGB", (columns * tile_width + (columns + 1) * gap, rows * tile_height + (rows + 1) * gap), "#CFCFCA")
    draw = ImageDraw.Draw(sheet)
    font = label_font(17)
    for index, (theme, files) in enumerate(previews.items()):
        x = gap + (index % columns) * (tile_width + gap)
        y = gap + (index // columns) * (tile_height + gap)
        draw.rectangle((x, y, x + tile_width, y + tile_height), fill="#FFFFFF", outline="#8F8F88", width=2)
        for page_index, file in enumerate(files):
            with Image.open(file).convert("RGB") as image:
                fitted = ImageOps.contain(image, page_thumb, method=Image.Resampling.LANCZOS)
                thumb = Image.new("RGB", page_thumb, "#F7F7F4")
                thumb.paste(fitted, ((page_thumb[0] - fitted.width) // 2, (page_thumb[1] - fitted.height) // 2))
            px = x + tile_padding + page_index * (page_thumb[0] + page_gap)
            py = y + tile_padding
            sheet.paste(thumb, (px, py))
        system = renderer.THEME_PRESETS[theme]["system"]
        label = f"{system} · {theme} · {renderer.THEME_LABELS[theme]}"
        draw.text((x + tile_padding, y + tile_padding + page_thumb[1] + 10), label, fill="#1A1A1A", font=font)
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, "JPEG", quality=91, optimize=True)
    return sheet.size


def run(args: argparse.Namespace) -> None:
    spec_path = Path(args.spec).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    spec = renderer.load_json(spec_path)
    renderer.validate_spec(spec)
    themes = parse_themes(args.themes)
    pages = parse_pages(args.pages, len(spec["pages"]))
    chrome = renderer.find_chrome(args.chrome)
    temp_root = Path(tempfile.mkdtemp(prefix="rednote-style-gallery-"))
    try:
        previews = render_previews(spec, spec_path, themes, pages, chrome, args.timeout, temp_root)
        size = build_gallery(previews, output_dir / "style-gallery.jpg")
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)
    manifest = {
        "sourceSpec": str(spec_path),
        "sourceSpecSha256": renderer.sha256(spec_path),
        "variants": [
            {"visualSystem": renderer.THEME_PRESETS[theme]["system"], "themePreset": theme, "name": renderer.THEME_LABELS[theme]}
            for theme in themes
        ],
        "previewPages": pages,
        "gallery": "style-gallery.jpg",
        "gallerySize": list(size),
    }
    (output_dir / "style-gallery.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"outputDir": str(output_dir), "variantCount": len(themes), "gallerySize": size}, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="社交视觉系统与主题预览")
    parser.add_argument("--spec", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--themes", help="逗号分隔的主题 ID；默认全部")
    parser.add_argument("--pages", default="1,2", help="每种主题预览哪些观点页，默认 1,2")
    parser.add_argument("--chrome")
    parser.add_argument("--timeout", type=float, default=30.0)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
