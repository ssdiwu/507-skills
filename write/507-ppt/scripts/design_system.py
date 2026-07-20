"""Shared, project-authored components and design tokens for 507-ppt."""
from __future__ import annotations

from typing import Any

DIRECTIONS: dict[str, dict[str, str]] = {
    "swiss": {"label": "瑞士风", "paper": "F7F7F2", "ink": "111111", "accent": "002FA7", "title_ea": "PingFang SC", "title_latin": "Helvetica", "body_ea": "PingFang SC", "body_latin": "Helvetica", "meta_ea": "Menlo", "meta_latin": "Menlo", "radius": "0px", "density": "compact"},
    "magazine": {"label": "杂志风", "paper": "F0E6D2", "ink": "1F1A14", "accent": "9C6B3F", "title_ea": "Songti SC", "title_latin": "Georgia", "body_ea": "PingFang SC", "body_latin": "Helvetica", "meta_ea": "Menlo", "meta_latin": "Menlo", "radius": "0px", "density": "editorial"},
    "cobalt": {"label": "钴蓝技术", "paper": "EEF4FB", "ink": "10233F", "accent": "1B5FBF", "title_ea": "PingFang SC", "title_latin": "Avenir Next", "body_ea": "PingFang SC", "body_latin": "Arial", "meta_ea": "Menlo", "meta_latin": "Menlo", "radius": "8px", "density": "compact"},
    "clay": {"label": "陶土叙事", "paper": "F7EEE7", "ink": "38261F", "accent": "B85C38", "title_ea": "Songti SC", "title_latin": "Georgia", "body_ea": "PingFang SC", "body_latin": "Arial", "meta_ea": "Menlo", "meta_latin": "Menlo", "radius": "16px", "density": "relaxed"},
    "forest": {"label": "森林研究", "paper": "EFF3EC", "ink": "18352C", "accent": "39735B", "title_ea": "PingFang SC", "title_latin": "Avenir Next", "body_ea": "PingFang SC", "body_latin": "Arial", "meta_ea": "Menlo", "meta_latin": "Menlo", "radius": "6px", "density": "relaxed"},
    "noir": {"label": "黑白声明", "paper": "F4F1EA", "ink": "171717", "accent": "C53D2E", "title_ea": "PingFang SC", "title_latin": "Helvetica", "body_ea": "PingFang SC", "body_latin": "Helvetica", "meta_ea": "Menlo", "meta_latin": "Menlo", "radius": "0px", "density": "compact"},
}

COMPONENTS: dict[str, tuple[str, ...]] = {
    "cover": ("title", "subtitle"),
    "section": ("title", "subtitle"),
    "image-text": ("title", "body", "asset"),
    "three-part": ("title", "items"),
    "comparison": ("title", "items"),
    "process": ("title", "items"),
    "metric": ("title", "metric", "body"),
    "quote": ("quote", "attribution"),
}


def direction(name: str) -> dict[str, str]:
    try:
        return DIRECTIONS[name]
    except KeyError as error:
        raise ValueError(f"unknown design direction: {name}") from error


def validate_deck(data: Any) -> list[str]:
    if not isinstance(data, dict):
        return ["input must be a JSON object"]
    deck = data.get("deck")
    if not isinstance(deck, dict) or any(not deck.get(key) for key in ("title", "audience", "scene", "durationMinutes")):
        return ["deck context incomplete"]
    slides = data.get("slides")
    if not isinstance(slides, list) or not slides:
        return ["slides must be a non-empty array"]
    errors: list[str] = []
    ids: set[str] = set()
    for index, slide in enumerate(slides, start=1):
        if not isinstance(slide, dict):
            errors.append(f"slide {index} must be an object")
            continue
        slide_id, kind = slide.get("id"), slide.get("kind")
        if not isinstance(slide_id, str) or not slide_id:
            errors.append(f"slide {index} requires a non-empty id")
        elif slide_id in ids:
            errors.append(f"slide id {slide_id!r} is duplicated")
        else:
            ids.add(slide_id)
        if kind not in COMPONENTS:
            errors.append(f"slide {slide_id or index} has unknown component {kind!r}")
            continue
        if not slide.get("goal"):
            errors.append(f"slide {slide_id or index} requires a goal")
        if not (slide.get("notes") or slide.get("noNotes") is True):
            errors.append(f"slide {slide_id or index} requires notes or noNotes=true")
        for field in COMPONENTS[kind]:
            if not slide.get(field):
                errors.append(f"slide {slide_id or index} component {kind} requires {field}")
        if kind in {"three-part", "process"} and (not isinstance(slide.get("items"), list) or len(slide["items"]) < 3):
            errors.append(f"slide {slide_id or index} component {kind} requires at least three items")
        if kind == "comparison" and (not isinstance(slide.get("items"), list) or len(slide["items"]) != 2):
            errors.append(f"slide {slide_id or index} component comparison requires exactly two items")
        if kind == "image-text" and not isinstance(slide.get("asset"), dict):
            errors.append(f"slide {slide_id or index} component image-text requires an asset object")
        elif kind == "image-text" and not slide["asset"].get("alt"):
            errors.append(f"slide {slide_id or index} image-text asset requires alt")
    return errors


def visible_strings(slide: dict[str, Any]) -> list[str]:
    """Return user-visible strings in deterministic order for carrier comparison."""
    values: list[str] = []
    for key in ("eyebrow", "title", "subtitle", "body", "metric", "quote", "attribution", "caption", "footer"):
        value = slide.get(key)
        if isinstance(value, str) and value:
            values.append(value)
    for item in slide.get("items", []):
        if isinstance(item, dict):
            for key in ("label", "title", "body"):
                value = item.get(key)
                if isinstance(value, str) and value:
                    values.append(value)
    return values
