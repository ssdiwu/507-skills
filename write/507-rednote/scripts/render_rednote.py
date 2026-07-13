#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
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
except ImportError as exc:  # pragma: no cover - 运行环境错误
    raise SystemExit("缺少 Pillow：python3 -m pip install Pillow") from exc

CSS_WIDTH = 750
CSS_HEIGHT = 1000
OUTPUT_SIZE = (1500, 2000)
PAGE_TYPES = {"cover", "article"}
LAYOUT_MODES = {"longform", "cards"}
BLOCK_TYPES = {"paragraph", "note", "quote", "image", "cards", "flow", "timeline"}
TONES = {"green", "blue", "purple", "red"}
IMAGE_POSITIONS = {"center", "top", "bottom", "left", "right", "center top", "center bottom", "left center", "right center"}
STYLE_LABELS = {
    "editorial-507": "507 编辑文档",
    "retro": "复古怀旧",
    "newspaper": "报纸",
    "mono": "极简黑白",
    "nature": "自然森系",
    "bluegrad": "蓝色渐变",
    "autumn": "秋日暖阳",
    "dark": "深夜暗色",
    "morandi": "莫兰迪",
    "cyber": "赛博朋克",
    "neubrutalism": "新野蛮主义",
    "vintage-film": "胶片复古",
    "memphis": "孟菲斯",
    "editorial": "杂志排版",
    "glass": "磨砂玻璃",
    "bento": "格子布局",
    "y2k": "千禧复古",
    "pink": "粉色渐变",
}
STYLE_PRESETS = {
    "editorial-507": {"paper": "#f2f8ef", "paperAlt": "#eaf4e8", "ink": "#173c2d", "muted": "#6f8679", "accent": "#37a84f", "accentDark": "#246d38", "line": "#a9cfad"},
    "retro": {"paper": "#F4ECD8", "paperAlt": "#E8DBC0", "ink": "#4A3F35", "muted": "#8B715F", "accent": "#C17F59", "accentDark": "#8B5A3C", "line": "#C9A27F"},
    "newspaper": {"paper": "#f5f0e8", "paperAlt": "#ede8e0", "ink": "#1a1a1a", "muted": "#665f56", "accent": "#8b0000", "accentDark": "#650000", "line": "#81786d"},
    "mono": {"paper": "#FFFFFF", "paperAlt": "#F0F0F0", "ink": "#000000", "muted": "#555555", "accent": "#000000", "accentDark": "#000000", "line": "#000000"},
    "nature": {"paper": "#F0F7F0", "paperAlt": "#E4F0E5", "ink": "#2D4739", "muted": "#6B8172", "accent": "#4CAF50", "accentDark": "#2D6A3F", "line": "#9BC7A0"},
    "bluegrad": {"paper": "#E3F2FD", "paperAlt": "#BBDEFB", "ink": "#0D4778", "muted": "#557D9F", "accent": "#2196F3", "accentDark": "#1565C0", "line": "#90CAF9"},
    "autumn": {"paper": "#FFF8F0", "paperAlt": "#FCE7D2", "ink": "#5D4E37", "muted": "#8B735D", "accent": "#E67E22", "accentDark": "#B94E00", "line": "#EFC08E"},
    "dark": {"paper": "#1a1a2e", "paperAlt": "#262642", "ink": "#e0e0e0", "muted": "#AAA6C5", "accent": "#a78bfa", "accentDark": "#c4b5fd", "line": "#5B4C88"},
    "morandi": {"paper": "#e8e0d8", "paperAlt": "#DDD2CA", "ink": "#5a5248", "muted": "#82796F", "accent": "#9b8ea0", "accentDark": "#766879", "line": "#B8A8B8"},
    "cyber": {"paper": "#0d0d1a", "paperAlt": "#17172B", "ink": "#00e5ff", "muted": "#7AAEB6", "accent": "#ff00ff", "accentDark": "#00e5ff", "line": "#5C2C7D"},
    "neubrutalism": {"paper": "#FFE566", "paperAlt": "#FFFFFF", "ink": "#000000", "muted": "#4A4300", "accent": "#FF3366", "accentDark": "#000000", "line": "#000000"},
    "vintage-film": {"paper": "#C8A882", "paperAlt": "#D9C1A1", "ink": "#2C1810", "muted": "#6F513E", "accent": "#8B6914", "accentDark": "#5B4000", "line": "#8B6914"},
    "memphis": {"paper": "#FFFFFF", "paperAlt": "#FFF7D6", "ink": "#1A1A1A", "muted": "#646464", "accent": "#FF3366", "accentDark": "#00A6D6", "line": "#1A1A1A"},
    "editorial": {"paper": "#FAFAFA", "paperAlt": "#F0F0F0", "ink": "#111111", "muted": "#666666", "accent": "#E63946", "accentDark": "#111111", "line": "#111111"},
    "glass": {"paper": "#667eea", "paperAlt": "#764ba2", "ink": "#FFFFFF", "muted": "#E1DFF5", "accent": "#FFD700", "accentDark": "#FFF1A8", "line": "#C8C7EF"},
    "bento": {"paper": "#F5F5F0", "paperAlt": "#E7E7E0", "ink": "#1A1A1A", "muted": "#686860", "accent": "#4ECDC4", "accentDark": "#167C77", "line": "#1A1A1A"},
    "y2k": {"paper": "#0D0D2B", "paperAlt": "#171743", "ink": "#00FFFF", "muted": "#7BB5C2", "accent": "#FF00FF", "accentDark": "#00FFFF", "line": "#6534A4"},
    "pink": {"paper": "#FFE5EC", "paperAlt": "#FFF5F7", "ink": "#5D3A4A", "muted": "#8B6574", "accent": "#FF6B9D", "accentDark": "#B43E69", "line": "#FFB3CC"},
}
THEME_DEFAULTS = STYLE_PRESETS["editorial-507"]


class SectionAuditParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.overflow_pages: list[int] = []
        self.sections: list[dict] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "section":
            return
        values = dict(attrs)
        if not values.get("data-page"):
            return
        page_number = int(values["data-page"])
        classes = (values.get("class") or "").split()
        self.sections.append({
            "page": page_number,
            "type": "cover" if "cover" in classes else "article",
            "heading": values.get("data-heading") or "",
            "sourceMap": values.get("data-source-map") or "",
            "fillRatio": float(values.get("data-fill-ratio") or 1),
        })
        if values.get("data-overflow") == "true":
            self.overflow_pages.append(page_number)


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
    tone = item.get("tone", "green")
    if tone not in TONES:
        die(f"{label}.tone 无效：{tone}")


def validate_block(block: object, label: str) -> None:
    if not isinstance(block, dict):
        die(f"{label} 必须是 object")
    block_type = block.get("type")
    if block_type not in BLOCK_TYPES:
        die(f"{label}.type 无效：{block_type}")
    allowed_by_type = {
        "paragraph": {"type", "text", "variant"},
        "note": {"type", "text"},
        "quote": {"type", "text"},
        "image": {"type", "src", "alt", "caption", "height", "fit", "position"},
        "cards": {"type", "items"},
        "flow": {"type", "items"},
        "timeline": {"type", "items"},
    }
    reject_unknown(block, allowed_by_type[block_type], label)
    if block_type in {"paragraph", "note", "quote"}:
        require_text(block.get("text"), f"{label}.text")
    if block_type == "paragraph" and block.get("variant", "body") not in {"body", "lead", "big", "muted"}:
        die(f"{label}.variant 无效：{block.get('variant')}")
    if block_type == "image":
        require_text(block.get("src"), f"{label}.src")
        height = block.get("height", 330)
        if not isinstance(height, int) or not 120 <= height <= 520:
            die(f"{label}.height 必须在 120–520")
        if block.get("fit", "contain") not in {"contain", "cover"}:
            die(f"{label}.fit 只能是 contain 或 cover")
        if block.get("position", "center") not in IMAGE_POSITIONS:
            die(f"{label}.position 无效：{block.get('position')}")
    if block_type in {"cards", "flow", "timeline"}:
        items = block.get("items")
        limits = {"cards": (1, 3), "flow": (2, 4), "timeline": (2, 5)}[block_type]
        if not isinstance(items, list) or not limits[0] <= len(items) <= limits[1]:
            die(f"{label}.items 数量必须在 {limits[0]}–{limits[1]}")
        for index, item in enumerate(items, start=1):
            validate_item(item, f"{label}.items[{index}]")


def validate_spec(spec: dict) -> None:
    reject_unknown(spec, {"title", "author", "avatar", "layoutMode", "stylePreset", "theme", "pages"}, "project")
    require_text(spec.get("title"), "title")
    layout_mode = spec.get("layoutMode", "longform")
    if layout_mode not in LAYOUT_MODES:
        die(f"layoutMode 无效：{layout_mode}；可选：{', '.join(LAYOUT_MODES)}")
    style_preset = spec.get("stylePreset", "editorial-507")
    if style_preset not in STYLE_PRESETS:
        die(f"stylePreset 无效：{style_preset}；可选：{', '.join(STYLE_PRESETS)}")
    pages = spec.get("pages")
    if not isinstance(pages, list) or not 2 <= len(pages) <= 20:
        die("pages 数量必须在 2–20")
    theme = spec.get("theme", {})
    if not isinstance(theme, dict):
        die("theme 必须是 object")
    reject_unknown(theme, set(THEME_DEFAULTS), "theme")
    for key, value in theme.items():
        if not isinstance(value, str) or not re.fullmatch(r"#[0-9A-Fa-f]{6}", value):
            die(f"theme.{key} 必须是 #RRGGBB")
    if not isinstance(pages[0], dict) or pages[0].get("type") != "cover":
        die("pages[1] 必须是唯一封面 cover")
    for page_index, page in enumerate(pages, start=1):
        label = f"pages[{page_index}]"
        if not isinstance(page, dict) or page.get("type") not in PAGE_TYPES:
            die(f"{label}.type 必须是 cover 或 article")
        if page["type"] == "cover":
            if page_index != 1:
                die(f"{label} 不得再次使用 cover")
            reject_unknown(page, {"type", "kicker", "title", "subtitle", "author", "image", "imagePosition"}, label)
            require_text(page.get("title"), f"{label}.title")
            if page.get("imagePosition", "center") not in IMAGE_POSITIONS:
                die(f"{label}.imagePosition 无效：{page.get('imagePosition')}")
        else:
            reject_unknown(page, {"type", "heading", "sourceMap", "closing", "blocks"}, label)
            if "heading" in page:
                require_text(page.get("heading"), f"{label}.heading")
            require_text(page.get("sourceMap"), f"{label}.sourceMap")
            blocks = page.get("blocks")
            if not isinstance(blocks, list) or not blocks:
                die(f"{label}.blocks 至少需要一项")
            for block_index, block in enumerate(blocks, start=1):
                validate_block(block, f"{label}.blocks[{block_index}]")


def rich_text(value: object) -> str:
    escaped = html.escape(str(value or ""), quote=True)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"==(.+?)==", r'<span class="accent">\1</span>', escaped)
    escaped = re.sub(r"`(.+?)`", r"<code>\1</code>", escaped)
    return escaped.replace("\n", "<br>")


def asset_data_uri(value: str | None, spec_dir: Path) -> str | None:
    if not value:
        return None
    if value.startswith("data:"):
        return value
    if value.startswith(("http://", "https://")):
        die(f"不接受远程图片 URL：{value}")
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = (spec_dir / path).resolve()
    if not path.is_file():
        die(f"图片不存在：{path}")
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def render_item(item: dict, class_name: str = "card") -> str:
    tone = item.get("tone", "green")
    tag = f'<span class="chip {tone}">{rich_text(item["tag"])}</span>' if item.get("tag") else ""
    title = f"<h3>{rich_text(item['title'])}</h3>" if item.get("title") else ""
    text = f"<p>{rich_text(item['text'])}</p>" if item.get("text") else ""
    return f'<div class="{class_name} tone-{tone}">{tag}{title}{text}</div>'


def render_block(block: dict, spec_dir: Path) -> str:
    block_type = block["type"]
    if block_type == "paragraph":
        variant = block.get("variant", "body")
        return f'<p class="paragraph {variant}">{rich_text(block["text"])}</p>'
    if block_type in {"note", "quote"}:
        return f'<div class="{block_type}">{rich_text(block["text"])}</div>'
    if block_type == "image":
        src = asset_data_uri(block["src"], spec_dir)
        alt = html.escape(block.get("alt", ""), quote=True)
        fit = block.get("fit", "contain")
        position = html.escape(block.get("position", "center"), quote=True)
        height = block.get("height", 330)
        caption = f'<div class="caption">{rich_text(block["caption"])}</div>' if block.get("caption") else ""
        return f'<div class="image-block"><img src="{src}" alt="{alt}" style="height:{height}px;object-fit:{fit};object-position:{position}">{caption}</div>'
    if block_type == "cards":
        cards = "".join(render_item(item) for item in block["items"])
        return f'<div class="cards cols-{len(block["items"])}">{cards}</div>'
    if block_type == "flow":
        parts: list[str] = []
        for index, item in enumerate(block["items"]):
            if index:
                parts.append('<div class="flow-arrow">→</div>')
            parts.append(render_item(item, "flow-card"))
        return f'<div class="flow">{"".join(parts)}</div>'
    items = "".join(render_item(item, "timeline-item") for item in block["items"])
    return f'<div class="timeline">{items}</div>'


def render_cover(page: dict, spec: dict, spec_dir: Path, avatar: str | None) -> str:
    image = asset_data_uri(page.get("image"), spec_dir)
    image_position = html.escape(page.get("imagePosition", "center"), quote=True)
    cover_image = f'<img class="cover-image" src="{image}" alt="" style="object-position:{image_position}">' if image else ""
    no_image = " no-image" if not image else ""
    kicker = f'<div class="kicker">{rich_text(page["kicker"])}</div>' if page.get("kicker") else ""
    subtitle = f'<div class="cover-sub">{rich_text(page["subtitle"])}</div>' if page.get("subtitle") else ""
    author = page.get("author") or spec.get("author", "")
    sign = f'<div class="cover-sign">{rich_text(author)}</div>' if author else ""
    avatar_html = f'<img class="avatar cover-avatar" src="{avatar}" alt="">' if avatar else ""
    return (
        f'<section class="page cover{no_image}" data-page="1" data-heading="{html.escape(page["title"], quote=True)}">{cover_image}'
        f'<div class="cover-body">{kicker}<h1>{rich_text(page["title"])}</h1>{subtitle}{sign}</div>'
        f'{avatar_html}</section>'
    )


def render_article(page: dict, page_index: int, body_number: int, spec_dir: Path, avatar: str | None) -> str:
    blocks = "".join(render_block(block, spec_dir) for block in page["blocks"])
    closing = " closing" if page.get("closing") else ""
    continuation = " continuation" if not page.get("heading") else ""
    heading = f'<h2>{rich_text(page["heading"])}</h2>' if page.get("heading") else ""
    source_map = html.escape(page.get("sourceMap", ""), quote=True)
    heading_attr = html.escape(page.get("heading", ""), quote=True)
    avatar_html = f'<img class="avatar" src="{avatar}" alt="">' if avatar else ""
    return (
        f'<section class="page article{closing}{continuation}" data-page="{page_index}" data-heading="{heading_attr}" data-source-map="{source_map}">'
        f'<div class="topbar"><span class="mark">✦</span><span class="pageno">{body_number:02d}</span></div>'
        f'{heading}<div class="blocks">{blocks}</div>{avatar_html}</section>'
    )


def render_flow_source(pages: list[dict], spec_dir: Path) -> str:
    units: list[str] = []
    for page in pages:
        source_map = html.escape(page.get("sourceMap", ""), quote=True)
        closing = "true" if page.get("closing") else "false"
        blocks = list(page["blocks"])
        if page.get("closing"):
            heading_value = page.get("heading", "")
            heading_attr = html.escape(heading_value, quote=True)
            heading_html = f'<h2>{rich_text(heading_value)}</h2>' if heading_value else ""
            prefix = blocks[:-3] if len(blocks) > 3 else []
            if prefix:
                first_prefix = render_block(prefix[0], spec_dir)
                chapter_class = " chapter-start" if heading_value else ""
                units.append(
                    f'<div class="flow-unit{chapter_class}" data-heading="{heading_attr}" data-source-map="{source_map}" data-closing="true">'
                    f'{heading_html}{first_prefix}</div>'
                )
                for block in prefix[1:]:
                    units.append(
                        f'<div class="flow-unit" data-heading="" data-source-map="{source_map}" data-closing="true">'
                        f'{render_block(block, spec_dir)}</div>'
                    )
                heading_attr = ""
                heading_html = ""
            closing_blocks = "".join(render_block(block, spec_dir) for block in blocks[len(prefix):])
            chapter_class = " chapter-start" if heading_html else ""
            units.append(
                f'<div class="flow-unit closing-group{chapter_class}" data-heading="{heading_attr}" data-source-map="{source_map}" data-closing="true">'
                f'{heading_html}{closing_blocks}</div>'
            )
            continue
        if page.get("heading"):
            heading = html.escape(page["heading"], quote=True)
            first_block = render_block(blocks.pop(0), spec_dir)
            units.append(
                f'<div class="flow-unit chapter-start" data-heading="{heading}" data-source-map="{source_map}" data-closing="{closing}">'
                f'<h2>{rich_text(page["heading"])}</h2>{first_block}</div>'
            )
        for block in blocks:
            units.append(
                f'<div class="flow-unit" data-heading="" data-source-map="{source_map}" data-closing="{closing}">'
                f'{render_block(block, spec_dir)}</div>'
            )
    return f'<div id="flow-source">{"".join(units)}</div>'


def render_flow_template(avatar: str | None) -> str:
    avatar_html = f'<img class="avatar" src="{avatar}" alt="">' if avatar else ""
    return (
        '<template id="flow-page-template"><section class="page article continuation" data-page="" data-heading="" data-source-map="">'
        '<div class="topbar"><span class="mark">✦</span><span class="pageno"></span></div>'
        f'<div class="flow-content"></div>{avatar_html}</section></template>'
    )


def render_html(spec: dict, spec_path: Path) -> str:
    spec_dir = spec_path.parent
    avatar = asset_data_uri(spec.get("avatar"), spec_dir)
    layout_mode = spec.get("layoutMode", "longform")
    style_preset = spec.get("stylePreset", "editorial-507")
    theme = {**STYLE_PRESETS[style_preset], **spec.get("theme", {})}
    theme_css = "\n".join(f"  --{re.sub(r'([A-Z])', lambda m: '-' + m.group(1).lower(), key)}: {value};" for key, value in theme.items())
    if layout_mode == "cards":
        sections: list[str] = []
        body_number = 0
        for page_index, page in enumerate(spec["pages"], start=1):
            if page["type"] == "cover":
                sections.append(render_cover(page, spec, spec_dir, avatar))
            else:
                body_number += 1
                sections.append(render_article(page, page_index, body_number, spec_dir, avatar))
    else:
        sections = [
            render_cover(spec["pages"][0], spec, spec_dir, avatar),
            render_flow_source(spec["pages"][1:], spec_dir),
            render_flow_template(avatar),
        ]
    title = html.escape(spec["title"], quote=True)
    return (HTML_TEMPLATE.replace("{{TITLE}}", title)
            .replace("{{STYLE}}", html.escape(style_preset, quote=True))
            .replace("{{LAYOUT}}", html.escape(layout_mode, quote=True))
            .replace("{{THEME}}", theme_css)
            .replace("{{SECTIONS}}", "\n".join(sections)))


def find_chrome(explicit: str | None) -> str:
    candidates = [
        explicit,
        os.environ.get("CHROME_PATH"),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        shutil.which("google-chrome"),
        shutil.which("google-chrome-stable"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(candidate)
    die("找不到 Chrome / Chromium；请设置 CHROME_PATH 或传 --chrome")


def base_chrome_command(chrome: str, profile: Path) -> list[str]:
    return [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--disable-background-networking",
        "--disable-component-update",
        "--disable-sync",
        "--no-first-run",
        "--no-default-browser-check",
        "--metrics-recording-only",
        "--force-device-scale-factor=2",
        f"--window-size={CSS_WIDTH},{CSS_HEIGHT}",
        f"--user-data-dir={profile}",
    ]


def inspect_layout(chrome: str, html_uri: str, timeout: float) -> SectionAuditParser:
    profile = Path(tempfile.mkdtemp(prefix="rednote-audit-"))
    dump_path = profile / "dump.html"
    log_path = profile / "chrome.log"
    command = base_chrome_command(chrome, profile) + ["--dump-dom", html_uri]
    process: subprocess.Popen | None = None
    try:
        with dump_path.open("wb") as output, log_path.open("wb") as log:
            process = subprocess.Popen(command, stdout=output, stderr=log, start_new_session=True)
            deadline = time.time() + timeout
            last_size = -1
            stable = 0
            while time.time() < deadline:
                if dump_path.exists() and dump_path.stat().st_size > 0:
                    size = dump_path.stat().st_size
                    stable = stable + 1 if size == last_size else 0
                    last_size = size
                    if stable >= 3 and b"</html>" in dump_path.read_bytes()[-2048:]:
                        break
                if process.poll() is not None:
                    break
                time.sleep(0.2)
        if not dump_path.exists() or b"</html>" not in dump_path.read_bytes()[-2048:]:
            details = log_path.read_text(encoding="utf-8", errors="ignore")[-1200:]
            die(f"Chrome 溢出检查失败或超时：{details}")
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


def audit_overflow(chrome: str, html_uri: str, timeout: float) -> list[int]:
    return inspect_layout(chrome, html_uri, timeout).overflow_pages


def render_png(chrome: str, html_uri: str, page_number: int, output: Path, timeout: float) -> None:
    profile = Path(tempfile.mkdtemp(prefix=f"rednote-page-{page_number:02d}-"))
    log_path = output.with_suffix(".chrome.log")
    command = base_chrome_command(chrome, profile) + [f"--screenshot={output}", f"{html_uri}?page={page_number}"]
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
                die(f"第 {page_number} 页渲染失败：{details}")
            if process.poll() is None:
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                    process.wait(timeout=2)
                except (ProcessLookupError, subprocess.TimeoutExpired):
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
    finally:
        log_path.unlink(missing_ok=True)
        shutil.rmtree(profile, ignore_errors=True)


def png_to_jpg(png_path: Path, jpg_path: Path) -> None:
    with Image.open(png_path).convert("RGB") as image:
        if image.size != OUTPUT_SIZE:
            die(f"渲染尺寸错误：{png_path}={image.size}，应为 {OUTPUT_SIZE}")
        image.save(jpg_path, "JPEG", quality=93, optimize=True, progressive=True)
    png_path.unlink()


def build_contact_sheet(files: list[Path], output: Path) -> None:
    thumb = (300, 400)
    label_height = 34
    columns = min(4, len(files))
    rows = math.ceil(len(files) / columns)
    gap = 18
    sheet = Image.new(
        "RGB",
        (columns * thumb[0] + (columns + 1) * gap, rows * (thumb[1] + label_height) + (rows + 1) * gap),
        "#cececa",
    )
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.load_default(size=20)
    except TypeError:  # Pillow < 10.1
        font = ImageFont.load_default()
    for index, file in enumerate(files):
        with Image.open(file).convert("RGB") as image:
            if image.size != OUTPUT_SIZE:
                die(f"图片尺寸错误：{file}={image.size}")
            tile = ImageOps.fit(image, thumb, method=Image.Resampling.LANCZOS)
        x = gap + (index % columns) * (thumb[0] + gap)
        y = gap + (index // columns) * (thumb[1] + label_height + gap)
        sheet.paste(tile, (x, y))
        draw.rectangle((x, y + thumb[1], x + thumb[0], y + thumb[1] + label_height), fill="#17251e")
        draw.text((x + 10, y + thumb[1] + 5), f"PAGE {index + 1:02d}", fill="white", font=font)
    sheet.save(output, "JPEG", quality=90, optimize=True)


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


def write_manifest(output_dir: Path, spec_path: Path, spec: dict, files: list[Path], selected_pages: list[int], page_map: list[dict]) -> None:
    manifest = {
        "status": "rendered",
        "sourceSpec": str(spec_path),
        "sourceSpecSha256": sha256(spec_path),
        "layoutMode": spec.get("layoutMode", "longform"),
        "stylePreset": spec.get("stylePreset", "editorial-507"),
        "html": "rednote.html",
        "htmlSha256": sha256(output_dir / "rednote.html"),
        "pageCount": len(files),
        "dimensions": list(OUTPUT_SIZE),
        "renderedPages": selected_pages,
        "contactSheet": "contact-sheet.jpg",
        "pageMap": page_map,
        "files": [
            {"page": index, "path": str(file.relative_to(output_dir)), "sha256": sha256(file)}
            for index, file in enumerate(files, start=1)
        ],
    }
    (output_dir / "render-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    spec_path = Path(args.spec).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    pages_dir = output_dir / "pages"
    output_dir.mkdir(parents=True, exist_ok=True)
    pages_dir.mkdir(parents=True, exist_ok=True)

    spec = load_json(spec_path)
    validate_spec(spec)
    html_text = render_html(spec, spec_path)
    html_path = output_dir / "rednote.html"
    html_path.write_text(html_text, encoding="utf-8")

    chrome = find_chrome(args.chrome)
    html_uri = html_path.resolve().as_uri()
    layout = inspect_layout(chrome, html_uri, args.timeout)
    if layout.overflow_pages:
        die(f"页面内容溢出，请先压缩文案或调整块高度：{layout.overflow_pages}")
    page_map = sorted(layout.sections, key=lambda item: item["page"])
    page_count = len(page_map)
    if [item["page"] for item in page_map] != list(range(1, page_count + 1)):
        die("渲染后的物理页码不连续")
    if args.pages:
        manifest_path = output_dir / "render-manifest.json"
        if not manifest_path.is_file():
            die("局部重渲染前必须先完成一次全量渲染")
        previous = load_json(manifest_path)
        if previous.get("pageCount") != page_count:
            die("自动分页结果已变化，不能局部重渲染；请执行全量渲染")
        if spec.get("layoutMode", "longform") == "longform" and previous.get("sourceSpecSha256") != sha256(spec_path):
            die("长文逻辑规格已变化，后续物理页可能整体位移；请执行全量渲染")
    selected_pages = parse_pages(args.pages, page_count)
    if not args.pages:
        for old in pages_dir.glob("rednote_page_*.*"):
            old.unlink()
    for page_number in selected_pages:
        png_path = pages_dir / f"rednote_page_{page_number:02d}.png"
        jpg_path = pages_dir / f"rednote_page_{page_number:02d}.jpg"
        png_path.unlink(missing_ok=True)
        render_png(chrome, html_uri, page_number, png_path, args.timeout)
        png_to_jpg(png_path, jpg_path)
        print(f"rendered page {page_number:02d}: {jpg_path}")

    files = [pages_dir / f"rednote_page_{index:02d}.jpg" for index in range(1, page_count + 1)]
    missing = [str(file) for file in files if not file.is_file()]
    if missing:
        die("局部重渲染前缺少其他页面：\n" + "\n".join(missing))
    build_contact_sheet(files, output_dir / "contact-sheet.jpg")
    write_manifest(output_dir, spec_path, spec, files, selected_pages, page_map)
    print(json.dumps({"outputDir": str(output_dir), "pages": page_count, "dimensions": OUTPUT_SIZE}, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="507-rednote 内部渲染脚本")
    parser.add_argument("--spec", required=True, help="rednote-project.json")
    parser.add_argument("--output-dir", required=True, help="作品下的小红书目录")
    parser.add_argument("--pages", help="只重渲染指定页，例如 3,5,7")
    parser.add_argument("--chrome", help="Chrome / Chromium 可执行文件")
    parser.add_argument("--timeout", type=float, default=25.0, help="每次浏览器操作超时秒数")
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
  --grid: color-mix(in srgb, var(--accent) 8%, transparent);
  --shadow: 0 20px 60px rgba(22,60,44,.14);
}
* { box-sizing: border-box; }
html, body { margin: 0; min-height: 100%; }
body { background:#d8d8d4; color:var(--ink); font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei","Noto Sans CJK SC",sans-serif; -webkit-font-smoothing:antialiased; }
.deck { display:grid; grid-template-columns:repeat(auto-fit,750px); justify-content:center; gap:32px; padding:32px; }
.page { position:relative; width:750px; height:1000px; overflow:hidden; padding:62px 64px 58px; background-color:var(--paper); background-image:linear-gradient(var(--grid) 1px,transparent 1px),linear-gradient(90deg,var(--grid) 1px,transparent 1px); background-size:42px 42px; box-shadow:var(--shadow); }
.page::after { content:""; position:absolute; inset:0; pointer-events:none; background:radial-gradient(circle at 72% 20%,rgba(255,255,255,.52),transparent 34%); }
.page > * { position:relative; z-index:1; }
.topbar { height:76px; display:flex; align-items:flex-start; justify-content:space-between; border-bottom:2px solid var(--line); margin-bottom:36px; }
.article.continuation .topbar { margin-bottom:24px; }
.article.continuation .blocks { padding-top:2px; }
#flow-source,#flow-page-template { display:none; }
.flow-content { display:grid; gap:17px; }
.flow-unit { display:grid; gap:17px; }
.flow-unit > * { margin:0; }
.flow-unit.chapter-start h2 { margin:0; }
.mark { color:var(--accent); font-size:28px; font-weight:900; line-height:1; }
.pageno { min-width:58px; padding:10px 14px; border-radius:16px; color:var(--accent); background:color-mix(in srgb,var(--accent) 12%,transparent); font-size:25px; font-weight:800; text-align:center; }
.avatar { position:absolute; right:40px; bottom:32px; z-index:3; width:62px; height:68px; object-fit:contain; image-rendering:pixelated; }
h1,h2,h3,p { margin-top:0; }
h1 { margin-bottom:24px; font-size:66px; line-height:1.12; letter-spacing:-.04em; }
h2 { margin-bottom:26px; color:var(--accent); font-size:43px; line-height:1.2; letter-spacing:-.025em; }
h3 { margin-bottom:10px; font-size:25px; line-height:1.3; }
p { margin-bottom:18px; font-size:24px; line-height:1.56; letter-spacing:.01em; }
strong,.accent { color:var(--accent-dark); font-weight:900; }
code { padding:2px 7px; border-radius:7px; background:rgba(0,0,0,.07); font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:.9em; }
.blocks { display:grid; gap:17px; }
.blocks > * { margin:0; }
.paragraph.lead { font-size:30px; line-height:1.5; }
.paragraph.big { font-size:36px; line-height:1.36; font-weight:800; }
.paragraph.muted { color:var(--muted); font-size:20px; }
.note { padding:18px 22px; border-left:6px solid var(--accent); border-radius:0 18px 18px 0; background:rgba(255,255,255,.68); font-size:21px; line-height:1.55; }
.quote { padding:24px 27px; border-radius:24px; background:var(--ink); color:#fff; font-size:33px; line-height:1.38; font-weight:800; text-align:center; }
.image-block img { display:block; width:100%; border:2px solid color-mix(in srgb,var(--ink) 15%,transparent); border-radius:22px; background:#fff; box-shadow:0 12px 32px rgba(23,60,45,.12); }
.caption { margin-top:9px; color:var(--muted); font-size:16px; line-height:1.4; }
.cards { display:grid; gap:16px; }
.cards.cols-2 { grid-template-columns:repeat(2,1fr); }
.cards.cols-3 { grid-template-columns:repeat(3,1fr); }
.card,.flow-card { padding:21px 22px; border:2px solid var(--line); border-radius:21px; background:rgba(255,255,255,.7); }
.card p,.flow-card p { margin:0; font-size:19px; line-height:1.48; }
.card h3,.flow-card h3 { margin-bottom:8px; }
.chip { display:inline-block; margin-bottom:10px; padding:6px 12px; border-radius:999px; color:var(--accent-dark); background:color-mix(in srgb,var(--accent) 16%,white); font-size:16px; font-weight:800; }
.tone-blue { border-color:#a8caec; background:#edf6ff; } .chip.blue { color:#0b5da8; background:#dcecff; }
.tone-purple { border-color:#c8baf1; background:#f2efff; } .chip.purple { color:#5433b0; background:#e9e2ff; }
.tone-red { border-color:#e5b5b2; background:#fff0ef; } .chip.red { color:#9e3939; background:#f9e1df; }
.flow { display:flex; gap:11px; align-items:stretch; }
.flow-card { flex:1; min-width:0; padding:18px 16px; }
.flow-arrow { display:grid; place-items:center; flex:0 0 28px; color:var(--accent); font-size:34px; font-weight:900; }
.timeline { position:relative; margin-left:12px; padding-left:34px; display:grid; gap:16px; }
.timeline::before { content:""; position:absolute; left:8px; top:8px; bottom:8px; width:3px; background:linear-gradient(var(--accent),#1479e8,#6f4cd6); }
.timeline-item { position:relative; }
.timeline-item::before { content:""; position:absolute; left:-34px; top:7px; width:16px; height:16px; border-radius:50%; border:4px solid var(--paper); background:var(--accent); box-shadow:0 0 0 2px var(--line); }
.timeline-item p { margin:0; color:var(--muted); font-size:19px; }
.closing .quote { font-size:37px; }
.cover { padding:0; }
.cover::after { display:none; }
.cover-image { display:block; width:100%; height:425px; object-fit:cover; }
.cover-body { height:575px; padding:52px 66px 56px; background-color:var(--paper); background-image:linear-gradient(var(--grid) 1px,transparent 1px),linear-gradient(90deg,var(--grid) 1px,transparent 1px); background-size:42px 42px; }
.cover.no-image .cover-body { height:1000px; padding-top:155px; }
.kicker { margin-bottom:24px; color:var(--accent-dark); font-size:18px; font-weight:800; letter-spacing:.08em; }
.cover h1 { max-width:620px; font-size:72px; }
.cover-sub { padding-top:22px; border-top:2px solid var(--line); color:var(--accent-dark); font-size:30px; line-height:1.45; font-weight:800; }
.cover-sign { position:absolute; left:66px; bottom:54px; color:var(--muted); font-size:20px; font-weight:700; }
.cover-avatar { width:94px; height:104px; right:48px; bottom:38px; }
/* style presets adapted from the local RedNoteImage theme system */
.theme-retro { font-family:"Noto Serif SC","Songti SC",serif; }
.theme-retro .page,.theme-retro .cover-body { background-color:var(--paper); background-image:radial-gradient(circle at 25px 25px,rgba(139,90,60,.12) 1px,transparent 1.5px); background-size:50px 50px; }
.theme-retro .topbar { border-bottom-style:dashed; }
.theme-retro h2 { font-family:"Noto Serif SC","Songti SC",serif; border-bottom:2px dashed var(--accent-dark); padding-bottom:10px; }
.theme-retro .quote { color:var(--accent-dark); background:rgba(193,127,89,.12); border:4px double var(--accent); font-family:"Noto Serif SC","Songti SC",serif; }
.theme-retro .cover h1 { color:var(--accent-dark); font-family:"Noto Serif SC","Songti SC",serif; text-decoration:underline; text-decoration-color:var(--accent); }

.theme-newspaper { font-family:"Noto Serif SC","Songti SC",serif; }
.theme-newspaper .page,.theme-newspaper .cover-body { background-color:var(--paper); background-image:repeating-linear-gradient(0deg,transparent,transparent 41px,rgba(0,0,0,.045) 41px,rgba(0,0,0,.045) 42px); }
.theme-newspaper .topbar { border-bottom:3px double var(--ink); }
.theme-newspaper .pageno { color:var(--ink); background:transparent; border-radius:0; }
.theme-newspaper h2 { color:var(--accent); font-family:"Noto Serif SC","Songti SC",serif; border-bottom:2px solid var(--ink); padding-bottom:10px; }
.theme-newspaper .note { background:rgba(139,0,0,.05); border-left-color:var(--accent); border-radius:0; }
.theme-newspaper .quote { color:var(--ink); background:transparent; border:3px double var(--ink); border-radius:0; font-family:"Noto Serif SC","Songti SC",serif; }
.theme-newspaper .cover h1 { color:var(--ink); font-family:"Noto Serif SC","Songti SC",serif; border-bottom:3px double var(--ink); padding-bottom:16px; }

.theme-mono { font-family:Inter,"PingFang SC",monospace; }
.theme-mono .page,.theme-mono .cover-body { background:#fff; background-image:none; }
.theme-mono .topbar { border-bottom:5px solid #000; }
.theme-mono .pageno { color:#fff; background:#000; border-radius:0; }
.theme-mono h2 { display:block; color:#fff; background:#000; padding:12px 16px; font-family:Inter,"PingFang SC",sans-serif; }
.theme-mono .note { color:#000; background:#fff; border:3px solid #000; border-left-width:8px; border-radius:0; }
.theme-mono .quote { color:#fff; background:#000; border:3px solid #000; border-radius:0; }
.theme-mono .card,.theme-mono .flow-card,.theme-mono .image-block img { border:4px solid #000; border-radius:0; box-shadow:none; }
.theme-mono .cover h1 { color:#000; border-top:5px solid #000; border-bottom:5px solid #000; padding:22px 0; text-transform:uppercase; }

.theme-nature .page,.theme-nature .cover-body { background-color:var(--paper); background-image:linear-gradient(90deg,rgba(76,175,80,.04) 1px,transparent 1px),linear-gradient(rgba(76,175,80,.04) 1px,transparent 1px); background-size:28px 28px; }
.theme-nature .quote { background:var(--accent-dark); }

.theme-bluegrad .page,.theme-bluegrad .cover-body { background:linear-gradient(180deg,var(--paper) 0%,var(--paper-alt) 100%); }
.theme-bluegrad h2,.theme-bluegrad .cover h1 { color:var(--accent-dark); }
.theme-bluegrad .quote { background:linear-gradient(135deg,#1976D2,#42A5F5); }
.theme-bluegrad .note { background:rgba(255,255,255,.48); }

.theme-autumn { font-family:"Noto Serif SC","Songti SC",serif; }
.theme-autumn .page,.theme-autumn .cover-body { background-color:var(--paper); background-image:radial-gradient(circle at 85% 15%,rgba(230,126,34,.12),transparent 28%); }
.theme-autumn h2 { font-family:"Noto Serif SC","Songti SC",serif; border-bottom:3px solid var(--accent); padding-bottom:10px; }
.theme-autumn .quote { background:var(--accent); }
.theme-autumn .cover h1 { color:var(--accent-dark); font-family:"Noto Serif SC","Songti SC",serif; }

.theme-dark .page,.theme-dark .cover-body { background:#1a1a2e; background-image:radial-gradient(circle at 75% 20%,rgba(124,58,237,.18),transparent 32%); }
.theme-dark .note,.theme-dark .card,.theme-dark .flow-card { color:var(--ink); background:rgba(255,255,255,.08); }
.theme-dark .quote { color:#fff; background:#5B3BB5; }
.theme-dark code { background:rgba(255,255,255,.12); }
.theme-dark .cover h1 { color:var(--accent); }

.theme-morandi { font-family:"Noto Serif SC","Songti SC",serif; }
.theme-morandi .page,.theme-morandi .cover-body { background:var(--paper); background-image:linear-gradient(135deg,rgba(255,255,255,.16),transparent 55%); }
.theme-morandi h2 { font-family:"Noto Serif SC","Songti SC",serif; font-weight:600; border-bottom:1px solid var(--line); padding-bottom:9px; }
.theme-morandi .quote { color:var(--ink); background:rgba(155,142,160,.18); border-left:5px solid var(--accent); font-style:italic; }
.theme-morandi .cover h1 { color:var(--accent-dark); font-family:"Noto Serif SC","Songti SC",serif; letter-spacing:.03em; }

.theme-cyber { font-family:Inter,"PingFang SC",monospace; }
.theme-cyber .page,.theme-cyber .cover-body { background:#0d0d1a; background-image:linear-gradient(rgba(0,229,255,.06) 1px,transparent 1px),linear-gradient(90deg,rgba(0,229,255,.06) 1px,transparent 1px); background-size:30px 30px; }
.theme-cyber .topbar { border-bottom-color:#00e5ff; }
.theme-cyber h2 { color:#00e5ff; text-shadow:0 0 12px rgba(0,229,255,.5); border-left:5px solid #ff00ff; padding-left:14px; }
.theme-cyber .note,.theme-cyber .card,.theme-cyber .flow-card { color:#00e5ff; background:rgba(0,229,255,.06); border-color:rgba(0,229,255,.45); }
.theme-cyber .quote { color:#00e5ff; background:rgba(255,0,255,.12); border:2px solid #ff00ff; box-shadow:0 0 18px rgba(255,0,255,.25); }
.theme-cyber .cover h1 { color:#00e5ff; text-shadow:0 0 14px #00e5ff; }

.theme-neubrutalism .page,.theme-neubrutalism .cover-body { background:#FFE566; background-image:none; }
.theme-neubrutalism .topbar { border-bottom:5px solid #000; }
.theme-neubrutalism .pageno { color:#fff; background:#FF3366; border:3px solid #000; border-radius:0; box-shadow:4px 4px 0 #000; }
.theme-neubrutalism h2 { color:#000; border-bottom:6px solid #000; padding-bottom:9px; text-shadow:3px 3px 0 #FF3366; }
.theme-neubrutalism .note,.theme-neubrutalism .card,.theme-neubrutalism .flow-card { color:#000; background:#fff; border:4px solid #000; border-radius:0; box-shadow:6px 6px 0 #000; }
.theme-neubrutalism .quote { color:#fff; background:#000; border:4px solid #000; border-radius:0; box-shadow:7px 7px 0 #FF3366; }
.theme-neubrutalism .cover h1 { color:#000; border:6px solid #000; padding:14px; box-shadow:9px 9px 0 #FF3366; }

.theme-vintage-film { font-family:"Noto Serif SC","Songti SC",serif; }
.theme-vintage-film .page,.theme-vintage-film .cover-body { background-color:#C8A882; background-image:repeating-radial-gradient(circle at 0 0,rgba(44,24,16,.05) 0,rgba(44,24,16,.05) 1px,transparent 1px,transparent 4px); }
.theme-vintage-film h2 { color:var(--ink); font-family:"Noto Serif SC","Songti SC",serif; border-bottom:3px solid var(--accent); padding-bottom:9px; }
.theme-vintage-film .quote { color:var(--ink); background:rgba(255,255,255,.18); border:5px double var(--accent); }
.theme-vintage-film .cover h1 { color:var(--ink); font-family:"Noto Serif SC","Songti SC",serif; border:7px solid var(--accent); padding:12px; }

.theme-memphis .page,.theme-memphis .cover-body { background-color:#fff; background-image:radial-gradient(circle at 12px 12px,rgba(255,51,102,.22) 3px,transparent 3.5px),radial-gradient(circle at 42px 42px,rgba(0,191,255,.18) 3px,transparent 3.5px); background-size:60px 60px; }
.theme-memphis .topbar { border-bottom:3px solid #1A1A1A; }
.theme-memphis .pageno { color:#fff; background:#00BFFF; border:2px solid #1A1A1A; border-radius:0; }
.theme-memphis h2 { color:#00A6D6; border-bottom:3px solid #1A1A1A; padding-bottom:9px; }
.theme-memphis .note,.theme-memphis .card,.theme-memphis .flow-card { background:rgba(255,255,255,.9); border:3px solid #1A1A1A; border-radius:5px; }
.theme-memphis .quote { background:#1A1A1A; color:#fff; border-radius:5px; box-shadow:7px 7px 0 #FF3366; }
.theme-memphis .cover h1 { color:#FF3366; border:3px solid #1A1A1A; padding:12px; background:rgba(255,255,255,.88); }

.theme-editorial .page,.theme-editorial .cover-body { background:#FAFAFA; background-image:linear-gradient(90deg,transparent 63px,rgba(17,17,17,.055) 64px,transparent 65px); background-size:128px 100%; }
.theme-editorial .topbar { border-bottom:4px solid #111; }
.theme-editorial .pageno { color:#fff; background:#111; border-radius:0; }
.theme-editorial h2 { color:#111; border-left:8px solid #E63946; padding-left:18px; }
.theme-editorial .note { color:#333; background:#F0F0F0; border-left-color:#111; border-radius:0; }
.theme-editorial .quote { color:#111; background:transparent; border-top:6px solid #111; border-bottom:6px solid #111; border-radius:0; text-align:left; }
.theme-editorial .cover h1 { color:#111; border-left:10px solid #E63946; padding-left:20px; }

.theme-glass .page,.theme-glass .cover-body { background:linear-gradient(135deg,#667eea 0%,#764ba2 100%); background-image:radial-gradient(circle at 20% 15%,rgba(255,255,255,.20),transparent 30%),linear-gradient(135deg,#667eea,#764ba2); }
.theme-glass .topbar { border-bottom-color:rgba(255,255,255,.38); }
.theme-glass .pageno { color:#FFD700; background:rgba(255,255,255,.16); border:1px solid rgba(255,255,255,.35); }
.theme-glass h2 { color:#FFD700; text-shadow:0 2px 8px rgba(0,0,0,.22); }
.theme-glass .note,.theme-glass .card,.theme-glass .flow-card { color:#fff; background:rgba(255,255,255,.14); border-color:rgba(255,255,255,.3); backdrop-filter:blur(10px); }
.theme-glass .quote { color:#241B48; background:#FFD700; }
.theme-glass .cover h1 { color:#fff; text-shadow:0 3px 12px rgba(0,0,0,.28); }

.theme-bento .page,.theme-bento .cover-body { background:#F5F5F0; background-image:none; }
.theme-bento .topbar { margin:-62px -64px 36px; height:106px; padding:34px 64px 0; color:#fff; background:#1A1A1A; border-bottom:0; }
.theme-bento .pageno { color:#1A1A1A; background:#4ECDC4; border-radius:8px; }
.theme-bento h2 { color:#1A1A1A; border-bottom:5px solid #4ECDC4; padding-bottom:10px; }
.theme-bento .note,.theme-bento .card,.theme-bento .flow-card { background:#fff; border:0; border-radius:18px; box-shadow:0 7px 0 #DADAD2; }
.theme-bento .quote { color:#fff; background:#1A1A1A; border-radius:18px; }
.theme-bento .cover h1 { color:#1A1A1A; border-bottom:7px solid #4ECDC4; padding-bottom:14px; }

.theme-y2k { font-family:Inter,"PingFang SC",monospace; }
.theme-y2k .page,.theme-y2k .cover-body { background:#0D0D2B; background-image:repeating-linear-gradient(0deg,transparent,transparent 39px,rgba(0,255,255,.06) 39px,rgba(0,255,255,.06) 40px),repeating-linear-gradient(90deg,transparent,transparent 39px,rgba(255,0,255,.05) 39px,rgba(255,0,255,.05) 40px); }
.theme-y2k .topbar { border-bottom-color:#FF00FF; }
.theme-y2k h2 { color:#00FFFF; border:2px solid #FF00FF; padding:11px; text-shadow:0 0 10px #00FFFF; }
.theme-y2k .note,.theme-y2k .card,.theme-y2k .flow-card { color:#00FFFF; background:rgba(255,0,255,.08); border-color:#FF00FF; }
.theme-y2k .quote { color:#0D0D2B; background:#00FFFF; border:4px solid #FF00FF; border-radius:0; box-shadow:7px 7px 0 #FF00FF; }
.theme-y2k .cover h1 { color:#FF00FF; text-shadow:0 0 14px #FF00FF; border:3px solid #00FFFF; padding:12px; }

.theme-pink .page,.theme-pink .cover-body { background:linear-gradient(135deg,#FFE5EC 0%,#FFF5F7 100%); }
.theme-pink h2 { color:#FF6B9D; }
.theme-pink .note { background:rgba(255,255,255,.56); border-left-color:#FF6B9D; }
.theme-pink .quote { color:#fff; background:linear-gradient(135deg,#FF6B9D,#FF8FB1); }
.theme-pink .cover h1 { color:#FF6B9D; text-shadow:3px 3px 0 rgba(255,107,157,.13); }

body.single { background:#fff; padding:0; overflow:hidden; }
body.single .deck { display:block; padding:0; }
body.single .page { display:none; box-shadow:none; }
body.single .page.selected { display:block; }
</style>
</head>
<body class="theme-{{STYLE}} layout-{{LAYOUT}}">
<main class="deck">{{SECTIONS}}</main>
<script>
(function () {
  function buildLongformPages() {
    if (!document.body.classList.contains('layout-longform')) return;
    var source = document.getElementById('flow-source');
    var template = document.getElementById('flow-page-template');
    var deck = document.querySelector('.deck');
    var current = null;
    var pageNumber = 2;
    var bodyNumber = 1;
    function createPage() {
      var page = template.content.firstElementChild.cloneNode(true);
      page.dataset.page = String(pageNumber++);
      page.querySelector('.pageno').textContent = String(bodyNumber++).padStart(2, '0');
      deck.insertBefore(page, source);
      return page;
    }
    function contentOf(page) { return page.querySelector('.flow-content'); }
    Array.from(source.children).forEach(function (unit) {
      if (!current) current = createPage();
      var clone = unit.cloneNode(true);
      contentOf(current).appendChild(clone);
      if (current.scrollHeight > current.clientHeight + 1) {
        clone.remove();
        if (!contentOf(current).children.length) {
          contentOf(current).appendChild(clone);
          current.dataset.overflow = 'true';
        } else {
          current = createPage();
          contentOf(current).appendChild(clone);
          if (current.scrollHeight > current.clientHeight + 1) current.dataset.overflow = 'true';
        }
      }
    });
    function fillRatioOf(page) {
      var content = contentOf(page);
      if (!content.lastElementChild) return 0;
      var pageRect = page.getBoundingClientRect();
      var contentRect = content.getBoundingClientRect();
      var lastRect = content.lastElementChild.getBoundingClientRect();
      var safeBottom = page.clientHeight - parseFloat(getComputedStyle(page).paddingBottom || 0);
      return (lastRect.bottom - contentRect.top) / (safeBottom - (contentRect.top - pageRect.top));
    }
    var articlePages = Array.from(deck.querySelectorAll('section.article'));
    articlePages.forEach(function (closingPage, index) {
      if (!closingPage.querySelector('.closing-group') || index < 2) return;
      var previous = articlePages[index - 1];
      var donor = articlePages[index - 2];
      var previousContent = contentOf(previous);
      var donorContent = contentOf(donor);
      var difference = Math.abs(fillRatioOf(donor) - fillRatioOf(previous));
      while (donorContent.children.length > 1) {
        var candidate = donorContent.lastElementChild;
        previousContent.insertBefore(candidate, previousContent.firstElementChild);
        var nextDifference = Math.abs(fillRatioOf(donor) - fillRatioOf(previous));
        if (previous.scrollHeight > previous.clientHeight + 1 || nextDifference >= difference) {
          donorContent.appendChild(candidate);
          break;
        }
        difference = nextDifference;
      }
    });
    Array.from(deck.querySelectorAll('section.article')).forEach(function (page) {
      var units = Array.from(page.querySelectorAll('.flow-unit'));
      var headingUnit = units.find(function (unit) { return unit.dataset.heading; });
      var maps = [];
      units.forEach(function (unit) {
        if (unit.dataset.sourceMap && !maps.includes(unit.dataset.sourceMap)) maps.push(unit.dataset.sourceMap);
        if (unit.dataset.closing === 'true') page.classList.add('closing');
      });
      page.dataset.sourceMap = maps.join(' | ');
      page.dataset.heading = headingUnit ? headingUnit.dataset.heading : '';
      page.classList.toggle('continuation', !(units[0] && units[0].dataset.heading));
    });
    source.remove();
    template.remove();
  }
  buildLongformPages();
  document.querySelectorAll('.page').forEach(function (node) {
    if (node.scrollHeight > node.clientHeight + 1) node.dataset.overflow = 'true';
    else if (!node.dataset.overflow) node.dataset.overflow = 'false';
    var content = node.querySelector('.flow-content, .blocks');
    if (content && content.lastElementChild) {
      var pageRect = node.getBoundingClientRect();
      var contentRect = content.getBoundingClientRect();
      var lastRect = content.lastElementChild.getBoundingClientRect();
      var safeBottom = node.clientHeight - parseFloat(getComputedStyle(node).paddingBottom || 0);
      var used = lastRect.bottom - contentRect.top;
      var available = safeBottom - (contentRect.top - pageRect.top);
      node.dataset.fillRatio = String(Math.max(0, Math.min(1, used / available)).toFixed(3));
    } else node.dataset.fillRatio = '1.000';
  });
  var page = Number(new URLSearchParams(location.search).get('page') || 0);
  if (page > 0) {
    document.body.classList.add('single');
    var selected = document.querySelector('.page[data-page="' + page + '"]');
    if (selected) selected.classList.add('selected');
  }
})();
</script>
</body>
</html>
'''


if __name__ == "__main__":
    main()
