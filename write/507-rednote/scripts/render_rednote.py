#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import html
import json
import math
import mimetypes
import os
import re
import shutil
import signal
import subprocess
import tempfile
import time
from html.parser import HTMLParser
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
except ImportError as exc:  # pragma: no cover - runtime dependency
    raise SystemExit("缺少 Pillow：python3 -m pip install Pillow") from exc


SCALE = 2
CANVASES = {
    "rednote": {"css": (750, 1000), "output": (1500, 2000)},
    "wechat-main": {"css": (1050, 450), "output": (2100, 900)},
    "wechat-share": {"css": (540, 540), "output": (1080, 1080)},
}
VISUAL_SYSTEMS = {"editorial", "swiss"}
COVER_LAYOUTS = {"type", "split", "image-led"}
ARTICLE_LAYOUTS = {"statement", "evidence", "comparison", "steps", "list", "data", "closing"}
BLOCK_TYPES = {"paragraph", "note", "quote", "image", "screenshot", "motion", "cards", "flow", "timeline"}
TONES = {"green", "blue", "purple", "red"}
DESTINATIONS = {"postBody", "companionCopy", "series", "notUsed"}
IMAGE_POSITIONS = {
    "center", "top", "bottom", "left", "right", "center top", "center bottom", "left center", "right center"
}

THEME_PRESETS = {
    "editorial-paper": {
        "label": "纸墨编辑",
        "system": "editorial",
        "colors": {"paper": "#F4F0E8", "paperAlt": "#E7DED0", "ink": "#171717", "muted": "#6E665C", "accent": "#A63C32", "accentDark": "#6F231D", "line": "#B8AA9B"},
    },
    "editorial-night": {
        "label": "夜刊",
        "system": "editorial",
        "colors": {"paper": "#171717", "paperAlt": "#242321", "ink": "#F1E8D5", "muted": "#B8AE9B", "accent": "#D1A34A", "accentDark": "#F0C76A", "line": "#645B50"},
    },
    "swiss-blue": {
        "label": "信号蓝",
        "system": "swiss",
        "colors": {"paper": "#F7F7F4", "paperAlt": "#E7E8E6", "ink": "#0A0A0A", "muted": "#666A6A", "accent": "#1F4ACC", "accentDark": "#16348F", "line": "#A9ADAF"},
    },
    "swiss-red": {
        "label": "编辑红",
        "system": "swiss",
        "colors": {"paper": "#FAF9F5", "paperAlt": "#ECEAE4", "ink": "#111111", "muted": "#686762", "accent": "#E23B2D", "accentDark": "#9F251D", "line": "#B3B1AA"},
    },
}
THEME_LABELS = {key: value["label"] for key, value in THEME_PRESETS.items()}
THEME_COLOR_KEYS = set(next(iter(THEME_PRESETS.values()))["colors"])


class SectionAuditParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.sections: list[dict] = []
        self.motions: list[dict] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "section" and values.get("data-target"):
            self.sections.append({
                "target": values["data-target"],
                "page": int(values["data-page"]) if values.get("data-page") else None,
                "type": values.get("data-type", "canvas"),
                "point": values.get("data-point", ""),
                "sourceMap": values.get("data-source-map", ""),
                "layout": values.get("data-layout", ""),
                "fillRatio": float(values.get("data-fill-ratio") or 0),
                "minFont": float(values.get("data-min-font") or 999),
                "titleGap": float(values.get("data-title-gap") or 999),
                "overflow": values.get("data-overflow") == "true",
            })
        if tag == "div" and values.get("data-motion-id") and values.get("data-motion-page"):
            self.motions.append({
                "id": values["data-motion-id"],
                "page": int(values["data-motion-page"]),
                "x": float(values.get("data-motion-x") or 0),
                "y": float(values.get("data-motion-y") or 0),
                "width": float(values.get("data-motion-width") or 0),
                "height": float(values.get("data-motion-height") or 0),
            })

    def failures(self) -> list[str]:
        failures: list[str] = []
        airy_layouts = {"statement", "type", "image-led"}
        for section in self.sections:
            target = section["target"]
            if section["overflow"]:
                failures.append(f"{target}: 内容溢出")
            if section["minFont"] < 15:
                failures.append(f"{target}: 最小字号 {section['minFont']:.1f}px 低于 15px")
            if section["titleGap"] < 12:
                failures.append(f"{target}: 标题与下一内容间距 {section['titleGap']:.1f}px 低于 12px")
            if target.startswith("rednote-") and section["layout"] not in airy_layouts and section["fillRatio"] < 0.52:
                failures.append(f"{target}: 内容仅覆盖画布高度的 {section['fillRatio']:.0%}")
        return failures


def die(message: str) -> None:
    raise SystemExit(message)


def load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        die(f"规格文件不存在：{path}")
    except json.JSONDecodeError as exc:
        die(f"规格 JSON 无效：{path}:{exc.lineno}:{exc.colno} {exc.msg}")
    if not isinstance(data, dict):
        die("规格根节点必须是 object")
    return data


def require_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        die(f"{label} 必须是非空字符串")
    return value.strip()


def reject_unknown(value: dict, allowed: set[str], label: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        die(f"{label} 含未知字段：{', '.join(unknown)}")


def validate_item(item: object, label: str) -> None:
    if not isinstance(item, dict):
        die(f"{label} 必须是 object")
    reject_unknown(item, {"tag", "title", "text", "tone"}, label)
    if not any(isinstance(item.get(key), str) and item[key].strip() for key in ("title", "text")):
        die(f"{label} 至少需要 title 或 text")
    if item.get("tone", "green") not in TONES:
        die(f"{label}.tone 无效：{item.get('tone')}")


def validate_media_fields(block: dict, label: str) -> None:
    require_text(block.get("src"), f"{label}.src")
    height = block.get("height", 330)
    if not isinstance(height, int) or not 120 <= height <= 620:
        die(f"{label}.height 必须在 120–620")
    if block.get("fit", "contain") not in {"contain", "cover"}:
        die(f"{label}.fit 只能是 contain 或 cover")
    if block.get("position", "center") not in IMAGE_POSITIONS:
        die(f"{label}.position 无效：{block.get('position')}")


def validate_block(block: object, label: str) -> None:
    if not isinstance(block, dict):
        die(f"{label} 必须是 object")
    block_type = block.get("type")
    if block_type not in BLOCK_TYPES:
        die(f"{label}.type 无效：{block_type}")
    allowed = {
        "paragraph": {"type", "text", "variant"},
        "note": {"type", "text"},
        "quote": {"type", "text"},
        "image": {"type", "src", "alt", "caption", "height", "fit", "position"},
        "screenshot": {"type", "src", "alt", "caption", "height", "chrome", "fit", "position"},
        "motion": {"type", "src", "alt", "caption", "height", "fit", "position", "startSec", "durationSec", "posterTimeSec"},
        "cards": {"type", "items"},
        "flow": {"type", "items"},
        "timeline": {"type", "items"},
    }
    reject_unknown(block, allowed[block_type], label)
    if block_type in {"paragraph", "note", "quote"}:
        require_text(block.get("text"), f"{label}.text")
    if block_type == "paragraph" and block.get("variant", "body") not in {"body", "lead", "big", "muted"}:
        die(f"{label}.variant 无效：{block.get('variant')}")
    if block_type in {"image", "screenshot", "motion"}:
        validate_media_fields(block, label)
    if block_type == "screenshot" and block.get("chrome", "none") not in {"none", "browser", "phone"}:
        die(f"{label}.chrome 无效：{block.get('chrome')}")
    if block_type == "motion":
        start = block.get("startSec", 0)
        duration = block.get("durationSec")
        poster = block.get("posterTimeSec", start)
        if not isinstance(start, (int, float)) or start < 0:
            die(f"{label}.startSec 必须 >= 0")
        if not isinstance(duration, (int, float)) or not 1 <= duration <= 5:
            die(f"{label}.durationSec 必须在 1–5 秒")
        if not isinstance(poster, (int, float)) or poster < start or poster > start + duration:
            die(f"{label}.posterTimeSec 必须位于选定片段内")
    if block_type in {"cards", "flow", "timeline"}:
        items = block.get("items")
        limits = {"cards": (1, 3), "flow": (2, 5), "timeline": (2, 5)}[block_type]
        if not isinstance(items, list) or not limits[0] <= len(items) <= limits[1]:
            die(f"{label}.items 数量必须在 {limits[0]}–{limits[1]}")
        for index, item in enumerate(items, start=1):
            validate_item(item, f"{label}.items[{index}]")


def validate_cover(page: dict, label: str, wechat: bool = False) -> None:
    allowed = {"type", "point", "sourceMap", "layout", "kicker", "title", "subtitle", "author", "image", "imagePosition"}
    reject_unknown(page, allowed, label)
    if not wechat and page.get("type") != "cover":
        die(f"{label}.type 必须是 cover")
    if wechat and "type" in page and page.get("type") != "cover":
        die(f"{label}.type 只能是 cover")
    require_text(page.get("point"), f"{label}.point")
    require_text(page.get("sourceMap"), f"{label}.sourceMap")
    require_text(page.get("title"), f"{label}.title")
    if page.get("layout") not in COVER_LAYOUTS:
        die(f"{label}.layout 无效：{page.get('layout')}")
    if page.get("imagePosition", "center") not in IMAGE_POSITIONS:
        die(f"{label}.imagePosition 无效：{page.get('imagePosition')}")


def validate_spec(spec: dict) -> None:
    legacy = sorted(set(spec) & {"layoutMode", "stylePreset"})
    if legacy:
        die(f"旧字段 {', '.join(legacy)} 已移除；请迁移为 visualSystem/themePreset 和显式观点页")
    allowed = {"title", "author", "avatar", "visualSystem", "themePreset", "theme", "excludedContent", "pages", "wechatCovers"}
    reject_unknown(spec, allowed, "project")
    require_text(spec.get("title"), "title")
    system = spec.get("visualSystem")
    if system not in VISUAL_SYSTEMS:
        die("visualSystem 必须是 editorial 或 swiss")
    preset = spec.get("themePreset")
    if preset not in THEME_PRESETS:
        die(f"themePreset 无效：{preset}")
    if THEME_PRESETS[preset]["system"] != system:
        die(f"themePreset {preset} 不属于 visualSystem {system}")
    theme = spec.get("theme", {})
    if not isinstance(theme, dict):
        die("theme 必须是 object")
    reject_unknown(theme, THEME_COLOR_KEYS, "theme")
    for key, value in theme.items():
        if not isinstance(value, str) or not re.fullmatch(r"#[0-9A-Fa-f]{6}", value):
            die(f"theme.{key} 必须是 #RRGGBB")
    excluded = spec.get("excludedContent")
    if not isinstance(excluded, list):
        die("excludedContent 必须是 array，可以为空")
    for index, item in enumerate(excluded, start=1):
        label = f"excludedContent[{index}]"
        if not isinstance(item, dict):
            die(f"{label} 必须是 object")
        reject_unknown(item, {"summary", "reason", "destination"}, label)
        require_text(item.get("summary"), f"{label}.summary")
        if item.get("destination") not in DESTINATIONS:
            die(f"{label}.destination 无效：{item.get('destination')}")
    pages = spec.get("pages")
    if not isinstance(pages, list) or not 2 <= len(pages) <= 20:
        die("pages 数量必须在 2–20")
    for page_index, page in enumerate(pages, start=1):
        label = f"pages[{page_index}]"
        if not isinstance(page, dict):
            die(f"{label} 必须是 object")
        if page_index == 1:
            validate_cover(page, label)
            continue
        if page.get("type") != "article":
            die(f"{label}.type 必须是 article")
        reject_unknown(page, {"type", "point", "sourceMap", "layout", "heading", "blocks"}, label)
        require_text(page.get("point"), f"{label}.point")
        require_text(page.get("sourceMap"), f"{label}.sourceMap")
        if page.get("layout") not in ARTICLE_LAYOUTS:
            die(f"{label}.layout 无效：{page.get('layout')}")
        if "heading" in page:
            require_text(page.get("heading"), f"{label}.heading")
        blocks = page.get("blocks")
        if not isinstance(blocks, list) or not blocks:
            die(f"{label}.blocks 至少需要一项")
        motions = 0
        for block_index, block in enumerate(blocks, start=1):
            validate_block(block, f"{label}.blocks[{block_index}]")
            motions += int(block.get("type") == "motion")
        if motions > 1:
            die(f"{label} 每页最多一个 motion")
    covers = spec.get("wechatCovers")
    if covers is not None:
        if not isinstance(covers, dict):
            die("wechatCovers 必须是 object")
        reject_unknown(covers, {"main", "share"}, "wechatCovers")
        if set(covers) != {"main", "share"}:
            die("wechatCovers 必须同时提供 main 和 share")
        validate_cover(covers["main"], "wechatCovers.main", wechat=True)
        validate_cover(covers["share"], "wechatCovers.share", wechat=True)


def rich_text(value: object) -> str:
    escaped = html.escape(str(value or ""), quote=True)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"==(.+?)==", r'<span class="accent">\1</span>', escaped)
    escaped = re.sub(r"`(.+?)`", r"<code>\1</code>", escaped)
    return escaped.replace("\n", "<br>")


def resolve_asset_path(value: str, spec_dir: Path, label: str) -> Path:
    if value.startswith(("http://", "https://", "data:")):
        die(f"{label} 只接受本地文件路径：{value}")
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = (spec_dir / path).resolve()
    if not path.is_file():
        die(f"{label} 不存在：{path}")
    return path


def asset_data_uri(value: str | None, spec_dir: Path) -> str | None:
    if not value:
        return None
    if value.startswith("data:"):
        return value
    path = resolve_asset_path(value, spec_dir, "图片")
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def run_command(command: list[str], label: str) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        details = (result.stderr or result.stdout)[-1600:]
        die(f"{label} 失败：{details}")
    return result


def find_binary(name: str, explicit: str | None = None) -> str:
    candidate = explicit or shutil.which(name)
    if not candidate or not Path(candidate).is_file():
        die(f"找不到 {name}；请先安装并加入 PATH")
    return str(candidate)


def probe_video(ffprobe: str, path: Path) -> dict:
    result = run_command([
        ffprobe, "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=codec_type,width,height:format=duration", "-of", "json", str(path),
    ], "ffprobe")
    data = json.loads(result.stdout)
    streams = data.get("streams") or []
    if not streams or streams[0].get("codec_type") != "video":
        die(f"视频没有可用画面流：{path}")
    try:
        duration = float(data["format"]["duration"])
    except (KeyError, TypeError, ValueError):
        die(f"无法读取视频时长：{path}")
    return {"duration": duration, "width": streams[0].get("width"), "height": streams[0].get("height")}


def prepare_motion_posters(spec: dict, spec_path: Path, temp_dir: Path, ffmpeg_path: str | None = None, ffprobe_path: str | None = None) -> tuple[dict, list[dict]]:
    prepared = copy.deepcopy(spec)
    motions: list[dict] = []
    motion_pages = [page for page in prepared["pages"] if page.get("type") == "article" and any(block.get("type") == "motion" for block in page["blocks"])]
    if not motion_pages:
        return prepared, motions
    ffmpeg = find_binary("ffmpeg", ffmpeg_path)
    ffprobe = find_binary("ffprobe", ffprobe_path)
    for page_number, page in enumerate(prepared["pages"], start=1):
        for block_index, block in enumerate(page.get("blocks", []), start=1):
            if block.get("type") != "motion":
                continue
            source = resolve_asset_path(block["src"], spec_path.parent, "motion.src")
            metadata = probe_video(ffprobe, source)
            start = float(block.get("startSec", 0))
            duration = float(block["durationSec"])
            poster_time = float(block.get("posterTimeSec", start))
            if start + duration > metadata["duration"] + 0.05:
                die(f"第 {page_number} 页视频片段超出源视频时长 {metadata['duration']:.3f}s")
            poster_path = temp_dir / f"motion-poster-{page_number:02d}.jpg"
            run_command([
                ffmpeg, "-y", "-ss", f"{poster_time:.3f}", "-i", str(source),
                "-frames:v", "1", "-q:v", "2", str(poster_path),
            ], f"第 {page_number} 页首帧提取")
            motion_id = f"motion-{page_number:02d}-{block_index:02d}"
            block["_poster"] = str(poster_path)
            block["_motionId"] = motion_id
            motions.append({
                "id": motion_id, "page": page_number, "source": source,
                "startSec": start, "durationSec": duration,
                "fit": block.get("fit", "cover"), "position": block.get("position", "center"),
                "sourceMetadata": metadata,
            })
    return prepared, motions


def render_item(item: dict, class_name: str = "card") -> str:
    tone = item.get("tone", "green")
    tag = f'<span class="chip {tone}">{rich_text(item["tag"])}</span>' if item.get("tag") else ""
    title = f"<h3>{rich_text(item['title'])}</h3>" if item.get("title") else ""
    text = f"<p>{rich_text(item['text'])}</p>" if item.get("text") else ""
    return f'<div class="{class_name} tone-{tone}">{tag}{title}{text}</div>'


def render_media_block(block: dict, spec_dir: Path) -> str:
    block_type = block["type"]
    source = block.get("_poster") if block_type == "motion" else block["src"]
    src = asset_data_uri(source, spec_dir)
    alt = html.escape(block.get("alt", ""), quote=True)
    fit = html.escape(block.get("fit", "contain"), quote=True)
    position = html.escape(block.get("position", "center"), quote=True)
    height = block.get("height", 330)
    caption = f'<div class="caption">{rich_text(block["caption"])}</div>' if block.get("caption") else ""
    image = f'<img class="media-frame" src="{src}" alt="{alt}" style="height:{height}px;object-fit:{fit};object-position:{position}">'
    if block_type == "image":
        return f'<figure class="image-block">{image}{caption}</figure>'
    if block_type == "screenshot":
        chrome = html.escape(block.get("chrome", "none"), quote=True)
        return f'<figure class="screenshot-block chrome-{chrome}">{image}{caption}</figure>'
    motion_id = html.escape(block.get("_motionId", ""), quote=True)
    if not motion_id:
        die("motion 必须先经过首帧准备再渲染")
    image = image.replace('class="media-frame"', 'class="media-frame motion-frame"')
    return f'<div class="motion-block" data-motion-id="{motion_id}">{image}{caption}</div>'


def render_block(block: dict, spec_dir: Path) -> str:
    block_type = block["type"]
    if block_type == "paragraph":
        return f'<p class="paragraph {block.get("variant", "body")}">{rich_text(block["text"])}</p>'
    if block_type in {"note", "quote"}:
        return f'<div class="{block_type}">{rich_text(block["text"])}</div>'
    if block_type in {"image", "screenshot", "motion"}:
        return render_media_block(block, spec_dir)
    if block_type == "cards":
        cards = "".join(render_item(item) for item in block["items"])
        return f'<div class="cards cols-{len(block["items"])}">{cards}</div>'
    if block_type == "flow":
        parts = "".join(render_item(item, "flow-card") for item in block["items"])
        return f'<div class="flow">{parts}</div>'
    items = "".join(render_item(item, "timeline-item") for item in block["items"])
    return f'<div class="timeline">{items}</div>'


def render_cover(page: dict, spec: dict, spec_dir: Path, avatar: str | None, target: str = "rednote-01") -> str:
    image = asset_data_uri(page.get("image"), spec_dir)
    position = html.escape(page.get("imagePosition", "center"), quote=True)
    media = f'<img class="cover-image" src="{image}" alt="" style="object-position:{position}">' if image else ""
    kicker = f'<div class="kicker">{rich_text(page["kicker"])}</div>' if page.get("kicker") else ""
    subtitle = f'<div class="cover-sub">{rich_text(page["subtitle"])}</div>' if page.get("subtitle") else ""
    author = page.get("author") or spec.get("author", "")
    sign = f'<div class="cover-sign">{rich_text(author)}</div>' if author else ""
    avatar_html = f'<img class="avatar cover-avatar" src="{avatar}" alt="">' if avatar else ""
    no_image = " no-image" if not image else ""
    return (
        f'<section class="canvas rednote page cover layout-{page["layout"]}{no_image}" data-target="{target}" data-page="1" '
        f'data-type="cover" data-point="{html.escape(page["point"], quote=True)}" '
        f'data-source-map="{html.escape(page["sourceMap"], quote=True)}" data-layout="{page["layout"]}">'
        f'{media}<div class="cover-body">{kicker}<h1>{rich_text(page["title"])}</h1>{subtitle}{sign}</div>{avatar_html}</section>'
    )


def render_article(page: dict, page_index: int, spec_dir: Path, avatar: str | None) -> str:
    blocks = "".join(render_block(block, spec_dir) for block in page["blocks"])
    heading = page.get("heading") or page["point"]
    avatar_html = f'<img class="avatar" src="{avatar}" alt="">' if avatar else ""
    return (
        f'<section class="canvas rednote page article layout-{page["layout"]}" data-target="rednote-{page_index:02d}" '
        f'data-page="{page_index}" data-type="article" data-point="{html.escape(page["point"], quote=True)}" '
        f'data-source-map="{html.escape(page["sourceMap"], quote=True)}" data-layout="{page["layout"]}">'
        f'<div class="topbar"><span class="mark">{html.escape(page["layout"].upper())}</span><span class="pageno">{page_index - 1:02d}</span></div>'
        f'<h2>{rich_text(heading)}</h2><div class="blocks">{blocks}</div>{avatar_html}</section>'
    )


def render_wechat_cover(page: dict, spec: dict, spec_dir: Path, avatar: str | None, target: str) -> str:
    image = asset_data_uri(page.get("image"), spec_dir)
    position = html.escape(page.get("imagePosition", "center"), quote=True)
    media = f'<img class="wechat-image" src="{image}" alt="" style="object-position:{position}">' if image else ""
    kicker = f'<div class="kicker">{rich_text(page["kicker"])}</div>' if page.get("kicker") else ""
    subtitle = f'<div class="wechat-sub">{rich_text(page["subtitle"])}</div>' if page.get("subtitle") else ""
    author = page.get("author") or spec.get("author", "")
    sign = f'<div class="cover-sign">{rich_text(author)}</div>' if author else ""
    avatar_html = f'<img class="avatar cover-avatar" src="{avatar}" alt="">' if avatar else ""
    return (
        f'<section class="canvas {target} layout-{page["layout"]}" data-target="{target}" data-type="wechat-cover" '
        f'data-point="{html.escape(page["point"], quote=True)}" data-source-map="{html.escape(page["sourceMap"], quote=True)}" '
        f'data-layout="{page["layout"]}">{media}<div class="wechat-body">{kicker}<h1>{rich_text(page["title"])}</h1>'
        f'{subtitle}{sign}</div>{avatar_html}</section>'
    )


def render_html(spec: dict, spec_path: Path) -> str:
    spec_dir = spec_path.parent
    avatar = asset_data_uri(spec.get("avatar"), spec_dir)
    preset = spec["themePreset"]
    colors = {**THEME_PRESETS[preset]["colors"], **spec.get("theme", {})}
    theme_css = "\n".join(f"  --{re.sub(r'([A-Z])', lambda m: '-' + m.group(1).lower(), key)}: {value};" for key, value in colors.items())
    sections = [render_cover(spec["pages"][0], spec, spec_dir, avatar)]
    sections.extend(render_article(page, index, spec_dir, avatar) for index, page in enumerate(spec["pages"][1:], start=2))
    if spec.get("wechatCovers"):
        sections.append(render_wechat_cover(spec["wechatCovers"]["main"], spec, spec_dir, avatar, "wechat-main"))
        sections.append(render_wechat_cover(spec["wechatCovers"]["share"], spec, spec_dir, avatar, "wechat-share"))
    return (HTML_TEMPLATE.replace("{{TITLE}}", html.escape(spec["title"], quote=True))
            .replace("{{SYSTEM}}", spec["visualSystem"])
            .replace("{{PRESET}}", preset)
            .replace("{{THEME}}", theme_css)
            .replace("{{SECTIONS}}", "\n".join(sections)))


def find_chrome(explicit: str | None) -> str:
    candidates = [
        explicit,
        os.environ.get("CHROME_PATH"),
        shutil.which("google-chrome"), shutil.which("google-chrome-stable"),
        shutil.which("chromium"), shutil.which("chromium-browser"),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        str(Path.home() / "Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(candidate)
    die("找不到 Chrome / Chromium；请设置 CHROME_PATH 或传 --chrome")


def base_chrome_command(chrome: str, profile: Path, css_size: tuple[int, int]) -> list[str]:
    return [
        chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
        "--disable-background-networking", "--disable-component-update", "--disable-sync",
        "--no-first-run", "--no-default-browser-check", "--metrics-recording-only",
        f"--force-device-scale-factor={SCALE}", f"--window-size={css_size[0]},{css_size[1]}",
        f"--user-data-dir={profile}",
    ]


def inspect_layout(chrome: str, html_uri: str, timeout: float) -> SectionAuditParser:
    profile = Path(tempfile.mkdtemp(prefix="rednote-audit-"))
    dump_path = profile / "dump.html"
    log_path = profile / "chrome.log"
    command = base_chrome_command(chrome, profile, (1200, 1200)) + ["--dump-dom", html_uri]
    process: subprocess.Popen | None = None
    try:
        with dump_path.open("wb") as output, log_path.open("wb") as log:
            process = subprocess.Popen(command, stdout=output, stderr=log, start_new_session=True)
            deadline = time.time() + timeout
            while time.time() < deadline:
                if process.poll() is not None:
                    break
                if dump_path.exists() and dump_path.stat().st_size and b"</html>" in dump_path.read_bytes()[-2048:]:
                    break
                time.sleep(0.2)
        if not dump_path.exists() or b"</html>" not in dump_path.read_bytes()[-2048:]:
            details = log_path.read_text(encoding="utf-8", errors="ignore")[-1200:]
            die(f"Chrome 布局检查失败或超时：{details}")
        parser = SectionAuditParser()
        parser.feed(dump_path.read_text(encoding="utf-8", errors="ignore"))
        return parser
    finally:
        if process and process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGTERM)
                process.wait(timeout=2)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        shutil.rmtree(profile, ignore_errors=True)


def render_png(chrome: str, html_uri: str, target: str, output: Path, css_size: tuple[int, int], timeout: float) -> None:
    profile = Path(tempfile.mkdtemp(prefix=f"rednote-{target}-"))
    log_path = output.with_suffix(".chrome.log")
    command = base_chrome_command(chrome, profile, css_size) + [f"--screenshot={output}", f"{html_uri}?target={target}"]
    process: subprocess.Popen | None = None
    try:
        with log_path.open("wb") as log:
            process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            deadline = time.time() + timeout
            last_size = -1
            stable = 0
            while time.time() < deadline:
                if output.exists() and output.stat().st_size > 0:
                    size = output.stat().st_size
                    stable = stable + 1 if size == last_size else 0
                    last_size = size
                    if stable >= 3:
                        break
                if process.poll() is not None and not output.exists():
                    break
                time.sleep(0.2)
            if not output.exists() or output.stat().st_size == 0:
                details = log_path.read_text(encoding="utf-8", errors="ignore")[-1200:]
                die(f"{target} 渲染失败：{details}")
    finally:
        if process and process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGTERM)
                process.wait(timeout=2)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        log_path.unlink(missing_ok=True)
        shutil.rmtree(profile, ignore_errors=True)


def png_to_jpg(png_path: Path, jpg_path: Path, output_size: tuple[int, int]) -> None:
    with Image.open(png_path).convert("RGB") as image:
        if image.size != output_size:
            die(f"渲染尺寸错误：{png_path}={image.size}，应为 {output_size}")
        image.save(jpg_path, "JPEG", quality=93, optimize=True, progressive=True)
    png_path.unlink()


def label_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in ("/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/STHeiti Medium.ttc"):
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size=size)
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def build_contact_sheet(files: list[Path], output: Path) -> None:
    thumb = (300, 400)
    label_height = 34
    columns = min(4, len(files))
    rows = math.ceil(len(files) / columns)
    gap = 18
    sheet = Image.new("RGB", (columns * thumb[0] + (columns + 1) * gap, rows * (thumb[1] + label_height) + (rows + 1) * gap), "#CECECA")
    draw = ImageDraw.Draw(sheet)
    font = label_font(20)
    for index, file in enumerate(files):
        with Image.open(file).convert("RGB") as image:
            tile = ImageOps.fit(image, thumb, method=Image.Resampling.LANCZOS)
        x = gap + (index % columns) * (thumb[0] + gap)
        y = gap + (index // columns) * (thumb[1] + label_height + gap)
        sheet.paste(tile, (x, y))
        draw.rectangle((x, y + thumb[1], x + thumb[0], y + thumb[1] + label_height), fill="#171717")
        draw.text((x + 10, y + thumb[1] + 5), f"PAGE {index + 1:02d}", fill="white", font=font)
    sheet.save(output, "JPEG", quality=90, optimize=True)


def build_wechat_preview(main_path: Path, share_path: Path, output: Path) -> tuple[int, int]:
    canvas = Image.new("RGB", (2400, 1200), "#E5E5E1")
    with Image.open(main_path).convert("RGB") as main_image, Image.open(share_path).convert("RGB") as share_image:
        main_image.thumbnail((1450, 720), Image.Resampling.LANCZOS)
        share_image.thumbnail((760, 760), Image.Resampling.LANCZOS)
        canvas.paste(main_image, (80, (1200 - main_image.height) // 2))
        canvas.paste(share_image, (1600, (1200 - share_image.height) // 2))
    canvas.save(output, "JPEG", quality=91, optimize=True)
    return canvas.size


def parse_pages(value: str | None, page_count: int) -> list[int]:
    if not value:
        return list(range(1, page_count + 1))
    try:
        pages = sorted({int(item.strip()) for item in value.split(",") if item.strip()})
    except ValueError:
        die("--pages 必须是逗号分隔的页码，例如 3,5,7")
    if not pages or pages[0] < 1 or pages[-1] > page_count:
        die(f"--pages 必须在 1–{page_count}")
    return pages


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_path(path: Path) -> str:
    if path.is_file():
        return sha256(path)
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(str(child.relative_to(path)).encode())
        digest.update(bytes.fromhex(sha256(child)))
    return digest.hexdigest()


def hash_json(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def global_spec_hash(spec: dict) -> str:
    return hash_json({key: spec.get(key) for key in ("title", "author", "avatar", "visualSystem", "themePreset", "theme", "excludedContent", "wechatCovers")})


def collect_source_assets(spec: dict, spec_path: Path) -> list[dict]:
    entries: list[dict] = []

    def add(role: str, value: str | None) -> None:
        if not value:
            return
        if value.startswith("data:"):
            entries.append({"role": role, "source": "data-uri", "sha256": hashlib.sha256(value.encode()).hexdigest()})
            return
        path = resolve_asset_path(value, spec_path.parent, role)
        entries.append({"role": role, "source": value, "sha256": sha256(path)})

    add("avatar", spec.get("avatar"))
    for page_index, page in enumerate(spec["pages"], start=1):
        add(f"pages[{page_index}].image", page.get("image"))
        for block_index, block in enumerate(page.get("blocks", []), start=1):
            if block.get("type") in {"image", "screenshot", "motion"}:
                add(f"pages[{page_index}].blocks[{block_index}].src", block.get("src"))
    for name, cover in (spec.get("wechatCovers") or {}).items():
        add(f"wechatCovers.{name}.image", cover.get("image"))
    return entries


def page_map_from_spec(spec: dict) -> list[dict]:
    return [
        {"page": index, "type": page["type"], "point": page["point"], "sourceMap": page["sourceMap"], "layout": page["layout"], "pageSpecSha256": hash_json(page)}
        for index, page in enumerate(spec["pages"], start=1)
    ]


def validate_partial_render(spec: dict, output_dir: Path, selected: list[int], source_assets: list[dict]) -> None:
    manifest_path = output_dir / "render-manifest.json"
    if not manifest_path.is_file():
        die("局部重渲染前必须先完成一次全量渲染")
    previous = load_json(manifest_path)
    current_map = page_map_from_spec(spec)
    if previous.get("globalSpecSha256") != global_spec_hash(spec):
        die("全局视觉或载体规格已变化，请执行全量渲染")
    if previous.get("sourceAssetsSha256") != hash_json(source_assets):
        die("源图片或视频内容已变化，请执行全量渲染")
    if previous.get("pageCount") != len(current_map):
        die("页数已变化，请执行全量渲染")
    old_by_page = {item["page"]: item for item in previous.get("pageMap", [])}
    for item in current_map:
        if item["page"] not in selected and old_by_page.get(item["page"], {}).get("pageSpecSha256") != item["pageSpecSha256"]:
            die(f"未选中的第 {item['page']} 页规格也已变化，请执行全量渲染")


def crop_expressions(position: str) -> tuple[str, str]:
    horizontal = "0" if "left" in position else "iw-ow" if "right" in position else "(iw-ow)/2"
    vertical = "0" if "top" in position else "ih-oh" if "bottom" in position else "(ih-oh)/2"
    return horizontal, vertical


def compose_motion_video(ffmpeg: str, base_jpg: Path, motion: dict, geometry: dict, output: Path) -> None:
    width = max(2, round(geometry["width"] * SCALE / 2) * 2)
    height = max(2, round(geometry["height"] * SCALE / 2) * 2)
    x = max(0, round(geometry["x"] * SCALE))
    y = max(0, round(geometry["y"] * SCALE))
    if motion["fit"] == "contain":
        slot = f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=white"
    else:
        crop_x, crop_y = crop_expressions(motion["position"])
        slot = f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}:{crop_x}:{crop_y}"
    filters = f"[1:v]{slot},setsar=1[slot];[0:v][slot]overlay={x}:{y}:shortest=1,format=yuv420p[v]"
    run_command([
        ffmpeg, "-y", "-loop", "1", "-i", str(base_jpg),
        "-ss", f"{motion['startSec']:.3f}", "-t", f"{motion['durationSec']:.3f}", "-i", str(motion["source"]),
        "-filter_complex", filters, "-map", "[v]", "-an", "-r", "30", "-t", f"{motion['durationSec']:.3f}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(output),
    ], f"第 {motion['page']} 页动态卡片合成")


def find_makelive(explicit: str | None) -> str:
    candidate = explicit or shutil.which("makelive")
    if not candidate or not Path(candidate).is_file():
        die("存在 motion 但找不到 makelive；请安装 makelive 0.6.2+ 并传 --makelive")
    return str(candidate)


def package_live_photo(makelive: str, key_photo: Path, movie: Path) -> tuple[Path, str]:
    expected = key_photo.with_suffix(".pvt")
    if expected.is_dir():
        shutil.rmtree(expected)
    elif expected.exists():
        expected.unlink()
    before = set(key_photo.parent.glob("*.pvt"))
    run_command([makelive, "--pvt", "--manual", str(key_photo), str(movie)], "Live Photo 打包")
    created = sorted(set(key_photo.parent.glob("*.pvt")) - before, key=lambda path: path.stat().st_mtime, reverse=True)
    package = expected if expected.exists() else created[0] if created else None
    if package is None:
        die("makelive 已返回成功，但未找到生成的 .pvt 包")
    images = sorted(path for path in package.iterdir() if path.suffix.lower() in {".jpg", ".jpeg", ".heic"})
    movies = sorted(path for path in package.iterdir() if path.suffix.lower() in {".mov", ".mp4"})
    if len(images) != 1 or len(movies) != 1:
        die(f"Live Photo 包内容无效：images={len(images)} movies={len(movies)}")
    check = run_command([makelive, "--check", "--manual", str(images[0]), str(movies[0])], "Live Photo 配对检查")
    match = re.search(r"are Live Photos:\s*(\S+)", check.stdout)
    if not match:
        die("makelive 未确认 .pvt 内的 JPG/MOV 是有效 Live Photo 配对")
    return package, match.group(1)


def artifact(kind: str, path: Path, output_dir: Path, dimensions: tuple[int, int] | None = None) -> dict:
    item = {"kind": kind, "path": str(path.relative_to(output_dir)), "sha256": sha256_path(path)}
    if dimensions:
        item["dimensions"] = list(dimensions)
    return item


def binary_version(command: str) -> str:
    result = subprocess.run([command, "-version"], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        result = subprocess.run([command, "--version"], capture_output=True, text=True, check=False)
    return (result.stdout or result.stderr).splitlines()[0][:200] if (result.stdout or result.stderr) else "unknown"


def write_manifest(output_dir: Path, spec_path: Path, spec: dict, artifacts: list[dict], selected_pages: list[int], motion_records: list[dict], tools: dict, source_assets: list[dict] | None = None) -> None:
    source_assets = collect_source_assets(spec, spec_path) if source_assets is None else source_assets
    manifest = {
        "status": "rendered",
        "sourceSpec": str(spec_path),
        "sourceSpecSha256": sha256(spec_path),
        "globalSpecSha256": global_spec_hash(spec),
        "sourceAssets": source_assets,
        "sourceAssetsSha256": hash_json(source_assets),
        "visualSystem": spec["visualSystem"],
        "themePreset": spec["themePreset"],
        "pageCount": len(spec["pages"]),
        "renderedPages": selected_pages,
        "pageMap": page_map_from_spec(spec),
        "excludedContent": spec["excludedContent"],
        "html": "rednote.html",
        "htmlSha256": sha256(output_dir / "rednote.html"),
        "artifacts": artifacts,
        "motion": motion_records,
        "tools": tools,
    }
    (output_dir / "render-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def render_static_targets(args: argparse.Namespace, spec: dict, html_path: Path, chrome: str, output_dir: Path, selected_pages: list[int]) -> tuple[list[Path], list[dict]]:
    pages_dir = output_dir / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    if not args.pages:
        for old in pages_dir.glob("rednote_page_*.*"):
            old.unlink()
    for page_number in selected_pages:
        png_path = pages_dir / f"rednote_page_{page_number:02d}.png"
        jpg_path = pages_dir / f"rednote_page_{page_number:02d}.jpg"
        png_path.unlink(missing_ok=True)
        render_png(chrome, html_path.as_uri(), f"rednote-{page_number:02d}", png_path, CANVASES["rednote"]["css"], args.timeout)
        png_to_jpg(png_path, jpg_path, CANVASES["rednote"]["output"])
        print(f"rendered page {page_number:02d}: {jpg_path}")
    files = [pages_dir / f"rednote_page_{index:02d}.jpg" for index in range(1, len(spec["pages"]) + 1)]
    missing = [str(file) for file in files if not file.is_file()]
    if missing:
        die("局部重渲染前缺少其他页面：\n" + "\n".join(missing))
    contact = output_dir / "contact-sheet.jpg"
    build_contact_sheet(files, contact)
    artifacts = [artifact("rednote-page", file, output_dir, CANVASES["rednote"]["output"]) for file in files]
    artifacts.append(artifact("rednote-contact-sheet", contact, output_dir))
    return files, artifacts


def render_wechat_targets(args: argparse.Namespace, spec: dict, html_path: Path, chrome: str, output_dir: Path) -> list[dict]:
    wechat_dir = output_dir / "wechat"
    if not args.pages and wechat_dir.is_dir():
        for old in wechat_dir.glob("wechat-*.*"):
            old.unlink()
    if not spec.get("wechatCovers"):
        return []
    wechat_dir.mkdir(parents=True, exist_ok=True)
    rendered: dict[str, Path] = {}
    artifacts: list[dict] = []
    for target, filename in (("wechat-main", "wechat-main.jpg"), ("wechat-share", "wechat-share.jpg")):
        png = wechat_dir / filename.replace(".jpg", ".png")
        jpg = wechat_dir / filename
        render_png(chrome, html_path.as_uri(), target, png, CANVASES[target]["css"], args.timeout)
        png_to_jpg(png, jpg, CANVASES[target]["output"])
        rendered[target] = jpg
        artifacts.append(artifact(target, jpg, output_dir, CANVASES[target]["output"]))
    preview = wechat_dir / "wechat-cover-pair.jpg"
    preview_size = build_wechat_preview(rendered["wechat-main"], rendered["wechat-share"], preview)
    artifacts.append(artifact("wechat-cover-pair", preview, output_dir, preview_size))
    return artifacts


def render_motion_targets(args: argparse.Namespace, motions: list[dict], layout: SectionAuditParser, page_files: list[Path], output_dir: Path) -> tuple[list[dict], list[dict], dict]:
    motion_dir = output_dir / "motion"
    if not args.pages and motion_dir.is_dir():
        for old in motion_dir.glob("rednote_page_*_live.*"):
            shutil.rmtree(old) if old.is_dir() else old.unlink()
    if not motions:
        return [], [], {}
    ffmpeg = find_binary("ffmpeg", args.ffmpeg)
    makelive = find_makelive(args.makelive)
    motion_dir.mkdir(parents=True, exist_ok=True)
    artifacts: list[dict] = []
    records: list[dict] = []
    geometry_by_id = {item["id"]: item for item in layout.motions}
    for motion in motions:
        geometry = geometry_by_id.get(motion["id"])
        if not geometry or geometry["width"] <= 0 or geometry["height"] <= 0:
            die(f"未获得第 {motion['page']} 页动态图片槽的真实布局坐标")
        stem = f"rednote_page_{motion['page']:02d}_live"
        key_photo = motion_dir / f"{stem}.jpg"
        movie = motion_dir / f"{stem}.mov"
        shutil.copy2(page_files[motion["page"] - 1], key_photo)
        compose_motion_video(ffmpeg, key_photo, motion, geometry, movie)
        package, asset_id = package_live_photo(makelive, key_photo, movie)
        artifacts.extend([
            artifact("live-photo-key", key_photo, output_dir, CANVASES["rednote"]["output"]),
            artifact("live-photo-mov", movie, output_dir, CANVASES["rednote"]["output"]),
            artifact("live-photo-package", package, output_dir),
        ])
        records.append({
            "status": "verified", "assetId": asset_id, "page": motion["page"], "slot": motion["id"],
            "source": str(motion["source"]), "sourceSha256": sha256(motion["source"]),
            "startSec": motion["startSec"], "durationSec": motion["durationSec"],
            "geometry": geometry, "keyPhoto": str(key_photo.relative_to(output_dir)),
            "movie": str(movie.relative_to(output_dir)), "package": str(package.relative_to(output_dir)),
        })
    return records, artifacts, {"ffmpeg": binary_version(ffmpeg), "makelive": binary_version(makelive)}


def run(args: argparse.Namespace) -> None:
    spec_path = Path(args.spec).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    spec = load_json(spec_path)
    validate_spec(spec)
    source_assets = collect_source_assets(spec, spec_path)
    has_motion = any(block.get("type") == "motion" for page in spec["pages"] for block in page.get("blocks", []))
    if args.pages and (has_motion or spec.get("wechatCovers")):
        die("含动态图片槽或公众号封面对时必须全量渲染")
    selected_pages = parse_pages(args.pages, len(spec["pages"]))
    if args.pages:
        validate_partial_render(spec, output_dir, selected_pages, source_assets)
    with tempfile.TemporaryDirectory(prefix="rednote-motion-") as temp:
        prepared, motions = prepare_motion_posters(spec, spec_path, Path(temp), args.ffmpeg, args.ffprobe)
        html_path = output_dir / "rednote.html"
        html_path.write_text(render_html(prepared, spec_path), encoding="utf-8")
        chrome = find_chrome(args.chrome)
        layout = inspect_layout(chrome, html_path.as_uri(), args.timeout)
        failures = layout.failures()
        expected_targets = {f"rednote-{index:02d}" for index in range(1, len(spec["pages"]) + 1)}
        actual_targets = {item["target"] for item in layout.sections if item["target"].startswith("rednote-")}
        if actual_targets != expected_targets:
            die(f"HTML 观点页与规格不一致：expected={sorted(expected_targets)} actual={sorted(actual_targets)}")
        if failures:
            die("浏览器布局检查失败：\n" + "\n".join(failures))
        page_files, artifacts = render_static_targets(args, spec, html_path, chrome, output_dir, selected_pages)
        artifacts.extend(render_wechat_targets(args, spec, html_path, chrome, output_dir))
        motion_records, motion_artifacts, media_tools = render_motion_targets(args, motions, layout, page_files, output_dir)
        artifacts.extend(motion_artifacts)
        artifacts.insert(0, artifact("single-file-html", html_path, output_dir))
        tools = {"chrome": binary_version(chrome), **media_tools}
        write_manifest(output_dir, spec_path, spec, artifacts, selected_pages, motion_records, tools, source_assets)
    print(json.dumps({"outputDir": str(output_dir), "pages": len(spec["pages"]), "visualSystem": spec["visualSystem"], "themePreset": spec["themePreset"]}, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="社交视觉包渲染脚本")
    parser.add_argument("--spec", required=True, help="rednote-project.json")
    parser.add_argument("--output-dir", required=True, help="作品下的小红书目录")
    parser.add_argument("--pages", help="只重渲染静态图卡指定页，例如 3,5")
    parser.add_argument("--chrome", help="Chrome / Chromium 可执行文件")
    parser.add_argument("--ffmpeg", help="ffmpeg 可执行文件")
    parser.add_argument("--ffprobe", help="ffprobe 可执行文件")
    parser.add_argument("--makelive", help="makelive 0.6.2+ 可执行文件")
    parser.add_argument("--timeout", type=float, default=30.0, help="每次浏览器操作超时秒数")
    run(parser.parse_args())


HTML_TEMPLATE = r'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{TITLE}}</title>
<style>
:root {
{{THEME}}
}
* { box-sizing:border-box; }
html,body { margin:0; min-height:100%; }
body { background:#D8D8D4; color:var(--ink); font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif; -webkit-font-smoothing:antialiased; }
.deck { display:flex; flex-wrap:wrap; justify-content:center; align-items:flex-start; gap:32px; padding:32px; }
.canvas { position:relative; overflow:hidden; flex:none; background:var(--paper); color:var(--ink); }
.rednote { width:750px; height:1000px; }
.wechat-main { width:1050px; height:450px; }
.wechat-share { width:540px; height:540px; }
.page { padding:58px 62px 52px; }
.page::before,.wechat-main::before,.wechat-share::before { content:""; position:absolute; inset:0; pointer-events:none; }
.visual-editorial .page::before,.visual-editorial .wechat-main::before,.visual-editorial .wechat-share::before { background-image:repeating-linear-gradient(0deg,transparent,transparent 31px,color-mix(in srgb,var(--line) 16%,transparent) 32px); }
.visual-swiss .page::before,.visual-swiss .wechat-main::before,.visual-swiss .wechat-share::before { background-image:linear-gradient(90deg,transparent 74px,color-mix(in srgb,var(--line) 18%,transparent) 75px,transparent 76px); background-size:150px 100%; }
.canvas > * { position:relative; z-index:1; }
h1,h2,h3,p,figure { margin:0; }
h1,h2 { letter-spacing:0; overflow-wrap:anywhere; }
h1 { font-size:70px; line-height:1.12; }
h2 { font-size:48px; line-height:1.18; margin-bottom:26px; }
h3 { font-size:26px; line-height:1.28; margin-bottom:8px; }
p { font-size:24px; line-height:1.52; }
strong,.accent { color:var(--accent-dark); font-weight:800; }
code { padding:2px 7px; background:var(--paper-alt); font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:.9em; }
.visual-editorial { font-family:"Songti SC","Noto Serif CJK SC",serif; }
.visual-editorial p,.visual-editorial .note,.visual-editorial .card { font-family:"PingFang SC","Microsoft YaHei",sans-serif; }
.visual-editorial h1,.visual-editorial h2 { font-weight:500; }
.visual-swiss { font-family:Inter,"Helvetica Neue","PingFang SC",sans-serif; }
.visual-swiss h1 { font-weight:300; }
.visual-swiss h2 { font-weight:400; }
.theme-editorial-night .canvas { background:var(--paper); }
.topbar { height:68px; display:flex; align-items:flex-start; justify-content:space-between; border-bottom:2px solid var(--line); margin-bottom:30px; }
.mark { color:var(--accent); font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:15px; font-weight:700; }
.pageno { min-width:52px; padding:8px 11px; color:var(--paper); background:var(--ink); font-size:20px; text-align:center; }
.blocks { display:grid; gap:17px; }
.paragraph.lead { font-size:30px; line-height:1.46; }
.paragraph.big { font-size:38px; line-height:1.3; font-weight:700; }
.paragraph.muted { color:var(--muted); font-size:19px; }
.note { padding:17px 20px; border-left:5px solid var(--accent); background:var(--paper-alt); font-size:21px; line-height:1.5; }
.quote { padding:22px 24px; border-top:3px solid var(--ink); border-bottom:3px solid var(--ink); font-size:31px; line-height:1.38; font-weight:700; }
.image-block img,.screenshot-block img,.motion-block img { display:block; width:100%; border:1px solid var(--line); background:#FFF; }
.visual-editorial .image-block img { border-radius:4px; }
.screenshot-block { padding:18px; background:var(--paper-alt); border:1px solid var(--line); }
.screenshot-block.chrome-browser::before { content:"●  ●  ●"; display:block; height:28px; color:var(--muted); font-size:12px; letter-spacing:8px; }
.screenshot-block.chrome-phone { max-width:72%; margin-inline:auto; padding:12px; border:8px solid var(--ink); border-radius:8px; }
.caption { margin-top:8px; color:var(--muted); font-size:15px; line-height:1.4; }
.cards { display:grid; gap:14px; }
.cards.cols-2 { grid-template-columns:repeat(2,1fr); }
.cards.cols-3 { grid-template-columns:repeat(3,1fr); }
.card,.flow-card { padding:18px 19px; border:1px solid var(--line); background:var(--paper-alt); }
.card p,.flow-card p { font-size:18px; line-height:1.45; }
.chip { display:inline-block; margin-bottom:9px; padding:4px 8px; color:var(--accent-dark); border:1px solid var(--accent); font-size:15px; font-weight:700; }
.flow { display:grid; gap:12px; }
.flow-card { border-left:5px solid var(--accent); }
.timeline { position:relative; padding-left:30px; display:grid; gap:16px; }
.timeline::before { content:""; position:absolute; left:7px; top:7px; bottom:7px; width:2px; background:var(--accent); }
.timeline-item::before { content:""; position:absolute; left:-29px; margin-top:7px; width:14px; height:14px; background:var(--accent); }
.timeline-item { position:relative; }
.timeline-item p { color:var(--muted); font-size:18px; }
.layout-statement h2 { font-size:62px; max-width:600px; }
.layout-statement .blocks { margin-top:70px; }
.layout-evidence .media-frame,.layout-evidence .screenshot-block { max-height:520px; }
.layout-comparison .cards { grid-template-columns:repeat(2,1fr); }
.layout-steps .blocks { min-height:600px; }
.layout-steps .flow { height:100%; grid-template-rows:repeat(auto-fit,minmax(120px,1fr)); }
.layout-steps .flow-card { min-height:120px; }
.layout-data .cards { grid-template-columns:repeat(3,1fr); }
.layout-closing h2 { font-size:58px; }
.layout-closing .quote { margin-top:50px; font-size:36px; }
.avatar { position:absolute; right:34px; bottom:26px; width:56px; height:60px; object-fit:contain; }
.cover { padding:0; }
.cover-image { display:block; width:100%; height:430px; object-fit:cover; }
.cover-body { height:570px; padding:50px 64px; display:flex; flex-direction:column; background:var(--paper); }
.cover.no-image .cover-body { height:1000px; padding-top:130px; }
.kicker { margin-bottom:22px; color:var(--accent); font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:16px; font-weight:700; text-transform:uppercase; }
.cover-sub,.wechat-sub { margin-top:24px; padding-top:20px; border-top:2px solid var(--line); color:var(--muted); font-size:27px; line-height:1.4; }
.cover-sign { margin-top:auto; color:var(--muted); font-size:18px; font-weight:700; }
.cover-avatar { width:82px; height:88px; }
.cover.layout-type .cover-image { display:none; }
.cover.layout-type .cover-body { height:1000px; padding-top:150px; }
.cover.layout-image-led .cover-image { height:1000px; }
.cover.layout-image-led .cover-body { position:absolute; inset:auto 0 0; height:auto; min-height:360px; color:#FFF; background:color-mix(in srgb,var(--ink) 78%,transparent); }
.cover.layout-image-led .cover-sub,.cover.layout-image-led .cover-sign { color:#EEE; border-color:#DDD; }
.wechat-main .wechat-image,.wechat-share .wechat-image { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }
.wechat-body { position:relative; height:100%; display:flex; flex-direction:column; padding:46px 58px; background:var(--paper); }
.wechat-main.layout-split .wechat-body { width:57%; border-right:2px solid var(--line); }
.wechat-main.layout-split .wechat-image { left:57%; width:43%; }
.wechat-main h1 { max-width:720px; font-size:58px; }
.wechat-share h1 { font-size:52px; }
.wechat-share .wechat-body { padding:52px; justify-content:center; }
.wechat-share .cover-sign { margin-top:26px; }
.wechat-main.layout-image-led .wechat-body,.wechat-share.layout-image-led .wechat-body { color:#FFF; background:color-mix(in srgb,var(--ink) 76%,transparent); }
.wechat-main.layout-image-led .wechat-body { width:58%; }
.wechat-share.layout-image-led .wechat-body { position:absolute; inset:auto 0 0; height:auto; min-height:52%; justify-content:flex-end; }
.wechat-main.layout-type .wechat-image,.wechat-share.layout-type .wechat-image { display:none; }
body.single { background:#FFF; overflow:hidden; }
body.single .deck { display:block; padding:0; }
body.single .canvas { display:none; }
body.single .canvas.selected { display:block; }
</style>
</head>
<body class="visual-{{SYSTEM}} theme-{{PRESET}}">
<main class="deck">{{SECTIONS}}</main>
<script>
(function () {
  function directText(node) {
    return Array.from(node.childNodes).some(function (child) { return child.nodeType === 3 && child.textContent.trim(); });
  }
  document.querySelectorAll('.canvas').forEach(function (canvas) {
    canvas.dataset.overflow = String(canvas.scrollHeight > canvas.clientHeight + 1 || canvas.scrollWidth > canvas.clientWidth + 1);
    var textNodes = Array.from(canvas.querySelectorAll('h1,h2,h3,p,.note,.quote,.caption,.kicker,.cover-sub,.wechat-sub,.cover-sign,.chip'));
    var fonts = textNodes.filter(directText).map(function (node) { return parseFloat(getComputedStyle(node).fontSize) || 999; });
    canvas.dataset.minFont = String(fonts.length ? Math.min.apply(null, fonts) : 999);
    var title = canvas.querySelector('h1,h2');
    var content = title && (title.nextElementSibling || canvas.querySelector('.blocks'));
    canvas.dataset.titleGap = String(title && content ? Math.max(0, content.getBoundingClientRect().top - title.getBoundingClientRect().bottom) : 999);
    var children = Array.from(canvas.children).filter(function (node) { return !node.classList.contains('avatar'); });
    var bottom = children.reduce(function (value, node) { return Math.max(value, node.getBoundingClientRect().bottom - canvas.getBoundingClientRect().top); }, 0);
    canvas.dataset.fillRatio = String(Math.max(0, Math.min(1, bottom / canvas.clientHeight)).toFixed(3));
    canvas.querySelectorAll('.motion-block').forEach(function (block) {
      var frame = block.querySelector('.motion-frame');
      var pageRect = canvas.getBoundingClientRect();
      var rect = frame.getBoundingClientRect();
      block.dataset.motionPage = canvas.dataset.page || '';
      block.dataset.motionX = String(rect.left - pageRect.left);
      block.dataset.motionY = String(rect.top - pageRect.top);
      block.dataset.motionWidth = String(rect.width);
      block.dataset.motionHeight = String(rect.height);
    });
  });
  var target = new URLSearchParams(location.search).get('target');
  if (target) {
    document.body.classList.add('single');
    var selected = document.querySelector('.canvas[data-target="' + target + '"]');
    if (selected) selected.classList.add('selected');
  }
})();
</script>
</body>
</html>
'''


if __name__ == "__main__":
    main()
