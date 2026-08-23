"""Shared phrase-aware text flow for HTML and PPTX renderers."""
from __future__ import annotations

from html import escape
from typing import Any

CLOSE_PUNCTUATION = set("，。；：！？、）】》〉」』”’…")
OPEN_PUNCTUATION = set("（【《〈「『“‘")


def validate_text_flow(text: str, spec: Any) -> list[str]:
    if spec in (None, {}):
        return []
    if not isinstance(spec, dict):
        return ["text flow must be an object"]
    units = spec.get("units")
    if not isinstance(units, list) or not units or any(not isinstance(item, str) or not item for item in units):
        return ["text flow units must be non-empty strings"]
    if "".join(units) != text:
        return ["text flow units must concatenate to visible text"]
    for index, unit in enumerate(units):
        if index and unit[0] in CLOSE_PUNCTUATION:
            return ["text flow unit cannot start with closing punctuation"]
        if index < len(units) - 1 and unit[-1] in OPEN_PUNCTUATION:
            return ["text flow unit cannot end with opening punctuation"]
    lines = spec.get("lines")
    if lines is not None:
        if not isinstance(lines, list) or not lines or any(not isinstance(item, str) or not item for item in lines):
            return ["text flow lines must be non-empty strings"]
        if "".join(lines) != text:
            return ["text flow lines must concatenate to visible text"]
        cursor = 0
        for line in lines:
            built = ""
            while cursor < len(units) and len(built) < len(line):
                built += units[cursor]
                cursor += 1
            if built != line:
                return ["text flow lines may break only between units"]
            if line[0] in CLOSE_PUNCTUATION:
                return ["text flow line cannot start with closing punctuation"]
            if line[-1] in OPEN_PUNCTUATION:
                return ["text flow line cannot end with opening punctuation"]
        if len(lines) > 1 and sum(character.isalnum() for character in lines[-1]) <= 2:
            return ["text flow cannot leave a one-or-two-character tail line"]
    max_lines = spec.get("maxLines")
    if max_lines is not None and (not isinstance(max_lines, int) or max_lines < 1):
        return ["text flow maxLines must be a positive integer"]
    if lines is not None and max_lines is not None and len(lines) > max_lines:
        return ["text flow lines exceed maxLines"]
    return []


def html_text(text: object, spec: dict[str, Any] | None = None) -> str:
    value = str(text or "")
    if not spec or not spec.get("units"):
        return escape(value)
    units = spec["units"]
    return "<wbr>".join(f'<span class="phrase">{escape(unit)}</span>' for unit in units)


def flow_classes(spec: dict[str, Any] | None, base: str = "") -> str:
    classes = [base] if base else []
    if spec and spec.get("units"):
        classes.append("phrase-aware")
    if spec and spec.get("preferSingleLine"):
        classes.append("prefer-single-line-intent")
        classes.append("prefer-single-line")
    return " ".join(classes)


def pptx_text(text: object, spec: dict[str, Any] | None = None) -> str:
    value = str(text or "")
    if not spec or not spec.get("lines"):
        return value
    return "\v".join(spec["lines"])
