#!/usr/bin/env python3
"""One-time migration from rednote-project.json to content.md + visual-plan.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from serve_rednote import atomic_write, default_visual_plan


LANGUAGE_MAP = {"editorial": "editorial-archive", "swiss": "precision-modern"}
PRESET_MAP = {
    "editorial-paper": "paper-archive",
    "editorial-night": "paper-archive",
    "swiss-blue": "signal-grid",
    "swiss-red": "current-editorial",
}


def markdown_block(block: dict) -> list[str]:
    kind = block.get("type")
    if kind == "paragraph":
        return [str(block.get("text", "")).strip()]
    if kind == "heading":
        level = int(block.get("level", 2))
        return [f"{'#' * max(2, min(3, level))} {str(block.get('text', '')).strip()}"]
    if kind == "list":
        ordered = bool(block.get("ordered"))
        return [f"{f'{index}. ' if ordered else '- '}{item}" for index, item in enumerate(block.get("items", []), start=1)]
    if kind in {"note", "quote"}:
        return [f"> {line}" for line in str(block.get("text", "")).splitlines()]
    if kind in {"image", "screenshot"}:
        alt = str(block.get("alt") or block.get("caption") or "图片")
        lines = [f"![{alt}]({block.get('src', '')})"]
        if block.get("caption") and block.get("caption") != alt:
            lines.append(str(block["caption"]))
        return lines
    if kind == "motion":
        raise ValueError("包含 motion 的旧规格不能静默迁移；请保留旧媒体后处理路径并人工确认 poster 与视频槽")
    raise ValueError(f"旧组件 {kind!r} 没有无损 Markdown 迁移路径")


def migrate(spec: dict) -> tuple[str, dict]:
    pages = spec.get("pages")
    if not isinstance(pages, list) or not pages:
        raise ValueError("旧规格缺少 pages")
    if spec.get("mode", "article") != "article":
        raise ValueError("首版迁移器只处理 article；summary 需要保留观点与排除项后单独迁移")
    cover = pages[0]
    lines = [f"# {cover.get('title') or spec.get('title') or '未命名作品'}"]
    if cover.get("subtitle"):
        lines.extend(["", f"> {cover['subtitle']}"])
    for page in pages[1:]:
        for block in page.get("blocks", []):
            rendered = markdown_block(block)
            if rendered:
                lines.extend(["", *rendered])
    content = "\n".join(lines).rstrip() + "\n"

    plan = default_visual_plan()
    plan["mode"] = "article"
    plan["designLanguage"] = LANGUAGE_MAP.get(spec.get("visualSystem"), "bold-statement")
    plan["presetId"] = PRESET_MAP.get(spec.get("themePreset"), "current-editorial")
    plan["cover"].update({
        "title": str(cover.get("title") or spec.get("title") or ""),
        "subtitle": str(cover.get("subtitle") or ""),
        "image": str(cover.get("image") or ""),
        "author": str(cover.get("author") or spec.get("author") or "507"),
    })
    plan["pageChrome"]["author"] = str(spec.get("author") or cover.get("author") or "507")
    return content, plan


def main() -> None:
    parser = argparse.ArgumentParser(description="迁移旧 rednote-project.json")
    parser.add_argument("--spec", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--force", action="store_true", help="覆盖已有 content.md 与 visual-plan.json")
    args = parser.parse_args()
    spec_path = Path(args.spec).expanduser().resolve()
    output = Path(args.output_dir).expanduser().resolve()
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    content, plan = migrate(spec)
    content_path = output / "content.md"
    plan_path = output / "visual-plan.json"
    if not args.force and (content_path.exists() or plan_path.exists()):
        raise SystemExit("目标已有 content.md 或 visual-plan.json；为防止覆盖，迁移已停止")
    output.mkdir(parents=True, exist_ok=True)
    atomic_write(content_path, content)
    atomic_write(plan_path, json.dumps(plan, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": "migrated", "content": str(content_path), "visualPlan": str(plan_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
