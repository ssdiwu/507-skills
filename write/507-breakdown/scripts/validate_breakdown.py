#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "assets" / "breakdown.schema.json"
VOCAB_PATH = ROOT / "references" / "tag-vocabulary.md"

# 词表分组与 breakdown.json 字段的映射关系，与 tag-vocabulary.md 的「分组与字段对应」表一致。
VISUAL_GROUPS = ("camera", "editing", "subtitle", "ui")


def load_grouped_tags(path: Path) -> dict[str, set[str]]:
    groups: dict[str, set[str]] = {}
    current: str | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        # 接受 `## group/` 、`## group/（中文）` 、`## group` 三种写法
        heading = re.match(r"^##\s+([a-z]+)(?:/|\s|$)", line.strip())
        if heading:
            current = heading.group(1)
            groups.setdefault(current, set())
            continue
        tag_match = re.match(r"^-\s+`([^`]+)`", line.strip())
        if tag_match and current:
            groups[current].add(tag_match.group(1))
    return groups


def require(condition: bool, message: str):
    if not condition:
        raise SystemExit(message)


def validate_breakdown(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    groups = load_grouped_tags(VOCAB_PATH)
    all_tags = set().union(*groups.values()) if groups else set()
    structure_tags = groups.get("structure", set())
    technique_tags = all_tags - structure_tags

    required = set(schema["required"])
    require(required.issubset(data.keys()), f"缺少必填字段：{sorted(required - set(data.keys()))}")
    require(data["videoType"] in schema["properties"]["videoType"]["enum"], f"非法 videoType：{data['videoType']!r}")
    require(isinstance(data["structure"], list), "structure 必须是数组")
    require(isinstance(data["segments"], list), "segments 必须是数组")

    # visualLanguage 子对象只能放同名分组的标签。
    visual_language = data.get("visualLanguage", {})
    require(isinstance(visual_language, dict), "visualLanguage 必须是对象")
    for group, items in visual_language.items():
        require(group in VISUAL_GROUPS, f"非法 visualLanguage 分组：{group}")
        require(isinstance(items, list), f"visualLanguage.{group} 必须是数组")
        allowed = groups.get(group, set())
        for item in items:
            require(item in allowed, f"非法 visualLanguage.{group} 标签：{item}（应属于 {group} 分组）")

    # segments.patterns 只能放 structure 分组；techniques 只能放非 structure 分组。
    for index, segment in enumerate(data["segments"], start=1):
        for field in ["start", "end", "transcript", "visualChange", "techniques", "patterns"]:
            require(field in segment, f"第 {index} 段缺少字段：{field}")
        for item in segment.get("patterns", []):
            require(item in structure_tags, f"第 {index} 段 patterns 非法标签：{item}（patterns 只能放 structure 分组）")
        for item in segment.get("techniques", []):
            require(item in technique_tags, f"第 {index} 段 techniques 非法标签：{item}（techniques 不能放 structure 分组）")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate 507-video-pull breakdown.json against schema basics and closed tag vocabulary")
    parser.add_argument("breakdown_json", help="Path to breakdown.json")
    args = parser.parse_args()
    validate_breakdown(Path(args.breakdown_json).expanduser().resolve())
    print("breakdown-validation-ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
