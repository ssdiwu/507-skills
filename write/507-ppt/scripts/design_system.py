"""Canonical semantic components, design languages, and visual presentations."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

TREATMENTS = ("default", "inverse", "section-emphasis", "dense")

DESIGN_LANGUAGES: dict[str, dict[str, Any]] = {
    "precision-modern": {
        "label": "精确现代主义",
        "paper": "F7F7F2", "ink": "111111", "muted": "5F646B", "accent": "002FA7", "surface": "FFFFFF", "line": "B8BBC0",
        "title_ea": "PingFang SC", "title_latin": "Helvetica", "body_ea": "PingFang SC", "body_latin": "Helvetica", "meta_ea": "Menlo", "meta_latin": "Menlo",
        "radius": "0px", "radius_cm": 0.0, "density": "compact", "grid": "strict", "surface_depth": "flat", "line_width": "1pt",
    },
    "editorial-archive": {
        "label": "编辑档案",
        "paper": "F0E6D2", "ink": "1F1A14", "muted": "67594D", "accent": "9C4F3B", "surface": "F7F0E4", "line": "B9A98E",
        "title_ea": "Songti SC", "title_latin": "Georgia", "body_ea": "PingFang SC", "body_latin": "Helvetica", "meta_ea": "Menlo", "meta_latin": "Menlo",
        "radius": "0px", "radius_cm": 0.0, "density": "editorial", "grid": "columns", "surface_depth": "paper", "line_width": "0.75pt",
    },
    "soft-product": {
        "label": "柔和产品",
        "paper": "EEF4FB", "ink": "10233F", "muted": "536A7D", "accent": "1B6F86", "surface": "FFFFFF", "line": "C3D2DF",
        "title_ea": "PingFang SC", "title_latin": "Avenir Next", "body_ea": "PingFang SC", "body_latin": "Avenir Next", "meta_ea": "Menlo", "meta_latin": "Menlo",
        "radius": "18px", "radius_cm": 0.32, "density": "relaxed", "grid": "modular", "surface_depth": "raised", "line_width": "0.5pt",
    },
    "warm-narrative": {
        "label": "温暖叙事",
        "paper": "F7EEE7", "ink": "38261F", "muted": "755F55", "accent": "B85C38", "surface": "FFF9F4", "line": "D8B9A8",
        "title_ea": "Songti SC", "title_latin": "Georgia", "body_ea": "PingFang SC", "body_latin": "Helvetica", "meta_ea": "Menlo", "meta_latin": "Menlo",
        "radius": "16px", "radius_cm": 0.28, "density": "relaxed", "grid": "asymmetric", "surface_depth": "paper", "line_width": "0.75pt",
    },
    "research-organic": {
        "label": "研究自然",
        "paper": "EFF3EC", "ink": "18352C", "muted": "526C62", "accent": "39735B", "surface": "F8FAF5", "line": "B8C9BF",
        "title_ea": "PingFang SC", "title_latin": "Avenir Next", "body_ea": "PingFang SC", "body_latin": "Helvetica", "meta_ea": "Menlo", "meta_latin": "Menlo",
        "radius": "8px", "radius_cm": 0.16, "density": "balanced", "grid": "modular", "surface_depth": "flat", "line_width": "0.75pt",
    },
    "bold-statement": {
        "label": "强声明",
        "paper": "F4F1EA", "ink": "171717", "muted": "5E5A55", "accent": "C53D2E", "surface": "FFFFFF", "line": "9E9992",
        "title_ea": "PingFang SC", "title_latin": "Helvetica", "body_ea": "PingFang SC", "body_latin": "Helvetica", "meta_ea": "Menlo", "meta_latin": "Menlo",
        "radius": "0px", "radius_cm": 0.0, "density": "compact", "grid": "poster", "surface_depth": "flat", "line_width": "1.25pt",
    },
}

PRESETS: dict[str, dict[str, str]] = {
    "swiss": {"label": "瑞士风", "language": "precision-modern", "variant": "default"},
    "magazine": {"label": "杂志风", "language": "editorial-archive", "variant": "default"},
    "cobalt": {"label": "钴蓝技术", "language": "soft-product", "variant": "default"},
    "clay": {"label": "陶土叙事", "language": "warm-narrative", "variant": "default"},
    "forest": {"label": "森林研究", "language": "research-organic", "variant": "default"},
    "noir": {"label": "黑白声明", "language": "bold-statement", "variant": "default"},
}

PRESENTATIONS: dict[str, dict[str, Any]] = {
    "type-led": {"label": "字体主导", "tier": "core", "carriers": {"html": "native", "pptx": "native"}},
    "panel-led": {"label": "面板主导", "tier": "core", "carriers": {"html": "native", "pptx": "native"}},
    "data-led": {"label": "数据主导", "tier": "core", "carriers": {"html": "native", "pptx": "native"}},
    "schematic-led": {"label": "示意图主导", "tier": "core", "carriers": {"html": "native", "pptx": "native"}},
    "photo-led": {"label": "摄影主导", "tier": "core", "carriers": {"html": "native", "pptx": "native"}, "requires": "asset"},
    "ui-product-led": {"label": "产品界面主导", "tier": "core", "carriers": {"html": "native", "pptx": "native"}, "requires": "ui-asset"},
    "editorial-print-led": {"label": "编辑印刷主导", "tier": "core", "carriers": {"html": "native", "pptx": "adapted"}},
    "hand-drawn-explainer": {"label": "手绘解释主导", "tier": "core", "carriers": {"html": "native", "pptx": "adapted"}},
}


def _presentations(preferred: tuple[str, ...], supported: tuple[str, ...] = (), conditional: tuple[str, ...] = ()) -> dict[str, str]:
    result = {name: "preferred" for name in preferred}
    result.update({name: "supported" for name in supported})
    result.update({name: "conditional" for name in conditional})
    return result


COMPONENTS: dict[str, dict[str, Any]] = {
    "cover": {"family": "identity", "required": ("title",), "presentations": _presentations(("type-led",), ("panel-led", "editorial-print-led"))},
    "section": {"family": "identity", "required": ("title",), "presentations": _presentations(("type-led", "editorial-print-led"), ("panel-led",))},
    "closing": {"family": "identity", "required": ("title",), "presentations": _presentations(("type-led",), ("panel-led", "editorial-print-led"))},
    "statement": {"family": "assertion", "required": ("title",), "presentations": _presentations(("type-led",), ("panel-led", "editorial-print-led"))},
    "collection": {"family": "set", "required": ("title", "items"), "presentations": _presentations(("panel-led",), ("schematic-led", "editorial-print-led", "hand-drawn-explainer"))},
    "comparison": {"family": "relation", "required": ("title", "items"), "presentations": _presentations(("panel-led", "schematic-led"), ("editorial-print-led", "hand-drawn-explainer"))},
    "sequence": {"family": "relation", "required": ("title", "items"), "presentations": _presentations(("schematic-led", "hand-drawn-explainer"), ("panel-led", "editorial-print-led"))},
    "relationship": {"family": "relation", "required": ("title", "nodes", "edges"), "presentations": _presentations(("schematic-led", "hand-drawn-explainer"), ("panel-led",))},
    "media-evidence": {"family": "evidence", "required": ("title", "assets"), "presentations": _presentations(("photo-led", "ui-product-led"))},
    "quote": {"family": "evidence", "required": ("quote", "attribution"), "presentations": _presentations(("type-led", "editorial-print-led"))},
    "metric": {"family": "data-evidence", "required": ("title", "data"), "presentations": _presentations(("data-led",), ("panel-led",))},
    "chart": {"family": "data-evidence", "required": ("title", "data"), "presentations": _presentations(("data-led",), ("panel-led", "editorial-print-led"))},
    "table": {"family": "data-evidence", "required": ("title", "data"), "presentations": _presentations(("data-led",), ("panel-led", "editorial-print-led")), "intrinsic_structure": "strong-lines", "suppresses": ("background-grid", "decorative-rules")},
}

LEGACY_COMPONENT_MAP = {"cover": "cover", "section": "section", "image-text": "media-evidence", "three-part": "collection", "comparison": "comparison", "process": "sequence", "metric": "metric", "quote": "quote"}
DIRECTIONS = PRESETS  # Compatibility alias retained for one migration window.


def language(name: str, treatment: str = "default") -> dict[str, Any]:
    if name not in DESIGN_LANGUAGES:
        raise ValueError(f"unknown design language: {name}")
    if treatment not in TREATMENTS:
        raise ValueError(f"unknown language treatment: {treatment}")
    result = deepcopy(DESIGN_LANGUAGES[name])
    result.update({"id": name, "treatment": treatment})
    if treatment == "inverse":
        original_paper = result["paper"]
        result["paper"], result["ink"] = result["ink"], result["paper"]
        result["surface"] = result["ink"]
        result["muted"] = original_paper
        result["line"] = original_paper
    elif treatment == "section-emphasis":
        result["surface"] = result["accent"]
    elif treatment == "dense":
        result["density"] = "dense"
    return result


def preset(name: str) -> dict[str, str]:
    if name not in PRESETS:
        raise ValueError(f"unknown preset: {name}")
    return deepcopy(PRESETS[name])


def direction(name: str) -> dict[str, Any]:
    selected = preset(name)
    result = language(selected["language"], selected["variant"])
    result.update({"preset": name, "label": selected["label"]})
    return result


def _component_id(slide: dict[str, Any]) -> str | None:
    component = slide.get("component")
    if isinstance(component, str):
        return component
    if isinstance(component, dict):
        component_type = component.get("type")
        if component_type == "data-evidence":
            return component.get("subtype")
        if isinstance(component_type, str):
            return component_type
    kind = slide.get("kind")
    return LEGACY_COMPONENT_MAP.get(kind) if isinstance(kind, str) else None


def normalize_deck(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError("input must be a JSON object")
    result = deepcopy(data)
    result["version"] = 3
    normalized: list[dict[str, Any]] = []
    for source in result.get("slides") or []:
        if not isinstance(source, dict):
            normalized.append(source)
            continue
        slide = deepcopy(source)
        slide["component"] = _component_id(slide)
        slide.pop("kind", None)
        if source.get("kind") == "image-text":
            asset = slide.pop("asset", None)
            caption = slide.pop("caption", None)
            if isinstance(asset, dict) and caption and not asset.get("caption"):
                asset["caption"] = caption
            if isinstance(asset, dict) and asset.get("id") == "workbench" and not asset.get("path"):
                asset["path"] = "assets/workbench.svg"
            slide["assets"] = [asset] if isinstance(asset, dict) else []
        elif source.get("kind") == "metric":
            slide["data"] = {"value": str(slide.pop("metric", "")), "label": str(slide.get("title") or "关键数字"), "context": str(slide.get("body") or "")}
        normalized.append(slide)
    result["slides"] = normalized
    return result


def _asset_roles(slide: dict[str, Any]) -> set[str]:
    return {str(asset.get("role") or "media") for asset in slide.get("assets") or [] if isinstance(asset, dict)}


def resolve_combination(component: str, presentation: str, language_id: str, carrier: str, slide: dict[str, Any] | None = None) -> dict[str, Any]:
    if component not in COMPONENTS:
        raise ValueError(f"unknown semantic component: {component}")
    if presentation not in PRESENTATIONS:
        raise ValueError(f"unknown visual presentation: {presentation}")
    language(language_id)
    state = COMPONENTS[component]["presentations"].get(presentation)
    if state is None:
        raise ValueError(f"presentation {presentation} is incompatible with component {component}")
    support = PRESENTATIONS[presentation]["carriers"].get(carrier, "unsupported")
    if support == "unsupported":
        raise ValueError(f"presentation {presentation} is unsupported for {carrier}")
    roles = _asset_roles(slide or {})
    requirement = PRESENTATIONS[presentation].get("requires")
    if requirement == "asset" and not roles:
        raise ValueError(f"presentation {presentation} requires an asset")
    if requirement == "ui-asset" and "ui" not in roles:
        raise ValueError(f"presentation {presentation} requires an asset with role=ui")
    suppressions = list(COMPONENTS[component].get("suppresses", ()))
    return {"compatibility": state, "carrierSupport": support, "suppressions": suppressions}


def preferred_presentation(component: str) -> str:
    if component not in COMPONENTS:
        raise ValueError(f"unknown semantic component: {component}")
    return next(name for name, state in COMPONENTS[component]["presentations"].items() if state == "preferred")


def validate_deck(data: Any) -> list[str]:
    try:
        normalized = normalize_deck(data)
    except ValueError as error:
        return [str(error)]
    deck = normalized.get("deck")
    if not isinstance(deck, dict) or any(not deck.get(key) for key in ("title", "audience", "scene", "durationMinutes")):
        return ["deck context incomplete"]
    slides = normalized.get("slides")
    if not isinstance(slides, list) or not slides:
        return ["slides must be a non-empty array"]
    errors: list[str] = []
    ids: set[str] = set()
    for index, slide in enumerate(slides, start=1):
        if not isinstance(slide, dict):
            errors.append(f"slide {index} must be an object")
            continue
        slide_id = slide.get("id")
        if not isinstance(slide_id, str) or not slide_id:
            errors.append(f"slide {index} requires a non-empty id")
            slide_id = str(index)
        elif slide_id in ids:
            errors.append(f"slide id {slide_id!r} is duplicated")
        else:
            ids.add(slide_id)
        component = slide.get("component")
        if component not in COMPONENTS:
            errors.append(f"slide {slide_id} has unknown component {component!r}")
            continue
        if not slide.get("goal"):
            errors.append(f"slide {slide_id} requires a goal")
        if not (slide.get("notes") or slide.get("noNotes") is True):
            errors.append(f"slide {slide_id} requires notes or noNotes=true")
        for field in COMPONENTS[component]["required"]:
            if slide.get(field) in (None, "", [], {}):
                errors.append(f"slide {slide_id} component {component} requires {field}")
        if component in {"collection", "sequence"} and isinstance(slide.get("items"), list) and not 2 <= len(slide["items"]) <= 6:
            errors.append(f"slide {slide_id} component {component} requires 2-6 items")
        if component == "comparison" and isinstance(slide.get("items"), list) and len(slide["items"]) != 2:
            errors.append(f"slide {slide_id} component comparison requires exactly two items")
        if component == "relationship":
            nodes, edges = slide.get("nodes"), slide.get("edges")
            if isinstance(nodes, list) and not 2 <= len(nodes) <= 8:
                errors.append(f"slide {slide_id} relationship requires 2-8 nodes")
            if isinstance(edges, list) and not 1 <= len(edges) <= 12:
                errors.append(f"slide {slide_id} relationship requires 1-12 edges")
        if component == "media-evidence" and isinstance(slide.get("assets"), list):
            if not 1 <= len(slide["assets"]) <= 3:
                errors.append(f"slide {slide_id} media-evidence requires 1-3 assets")
            asset_ids: set[str] = set()
            for asset in slide["assets"]:
                if not isinstance(asset, dict) or not asset.get("alt"):
                    errors.append(f"slide {slide_id} media-evidence assets require alt")
                    continue
                if not isinstance(asset.get("path"), str) or not asset["path"]:
                    errors.append(f"slide {slide_id} media-evidence assets require path")
                if not asset.get("id") or asset["id"] in asset_ids:
                    errors.append(f"slide {slide_id} media-evidence asset ids must be unique")
                else:
                    asset_ids.add(asset["id"])
        data_block = slide.get("data") if isinstance(slide.get("data"), dict) else {}
        if component == "metric" and any(data_block.get(key) in (None, "") for key in ("value", "label")):
            errors.append(f"slide {slide_id} metric requires data.value and data.label")
        if component == "chart":
            if data_block.get("chartType") not in ("bar", "line"):
                errors.append(f"slide {slide_id} chart supports chartType bar or line")
            categories, series = data_block.get("categories"), data_block.get("series")
            if not isinstance(categories, list) or not 2 <= len(categories) <= 8:
                errors.append(f"slide {slide_id} chart requires 2-8 categories")
            if not isinstance(series, list) or not 1 <= len(series) <= 3:
                errors.append(f"slide {slide_id} chart requires 1-3 series")
            elif isinstance(categories, list):
                for item in series:
                    if not isinstance(item, dict) or not item.get("name") or len(item.get("values") or []) != len(categories):
                        errors.append(f"slide {slide_id} chart series must match categories")
        if component == "table":
            columns, rows = data_block.get("columns"), data_block.get("rows")
            if not isinstance(columns, list) or not 2 <= len(columns) <= 5:
                errors.append(f"slide {slide_id} table requires 2-5 columns")
            if not isinstance(rows, list) or not 1 <= len(rows) <= 8:
                errors.append(f"slide {slide_id} table requires 1-8 rows")
            elif isinstance(columns, list) and any(not isinstance(row, list) or len(row) != len(columns) for row in rows):
                errors.append(f"slide {slide_id} table rows must match columns")
    return errors


def visible_text_paths(slide: dict[str, Any]) -> dict[str, str]:
    values: dict[str, str] = {}
    for key in ("eyebrow", "title", "subtitle", "body", "cta", "quote", "attribution", "caption", "footer"):
        value = slide.get(key)
        if value not in (None, ""):
            values[f"/{key}"] = str(value)
    for index, item in enumerate(slide.get("items") or []):
        if isinstance(item, dict):
            for key in ("label", "title", "body"):
                if item.get(key) not in (None, ""):
                    values[f"/items/{index}/{key}"] = str(item[key])
    for index, node in enumerate(slide.get("nodes") or []):
        if isinstance(node, dict):
            for key in ("label", "body"):
                if node.get(key) not in (None, ""):
                    values[f"/nodes/{index}/{key}"] = str(node[key])
    for index, edge in enumerate(slide.get("edges") or []):
        if isinstance(edge, dict):
            for key in ("from", "to", "label"):
                if edge.get(key) not in (None, ""):
                    values[f"/edges/{index}/{key}"] = str(edge[key])
    for index, asset in enumerate(slide.get("assets") or []):
        if isinstance(asset, dict):
            for key in ("caption", "label"):
                if asset.get(key) not in (None, ""):
                    values[f"/assets/{index}/{key}"] = str(asset[key])
    data = slide.get("data") if isinstance(slide.get("data"), dict) else {}
    for key in ("label", "value", "context", "source", "unit"):
        if data.get(key) not in (None, ""):
            values[f"/data/{key}"] = str(data[key])
    for index, item in enumerate(data.get("categories") or []):
        values[f"/data/categories/{index}"] = str(item)
    for series_index, series in enumerate(data.get("series") or []):
        if isinstance(series, dict):
            if series.get("name"):
                values[f"/data/series/{series_index}/name"] = str(series["name"])
            for value_index, item in enumerate(series.get("values") or []):
                values[f"/data/series/{series_index}/values/{value_index}"] = str(item)
    for index, item in enumerate(data.get("columns") or []):
        values[f"/data/columns/{index}"] = str(item)
    for row_index, row in enumerate(data.get("rows") or []):
        if isinstance(row, list):
            for column_index, item in enumerate(row):
                values[f"/data/rows/{row_index}/{column_index}"] = str(item)
    return values


def visible_strings(slide: dict[str, Any]) -> list[str]:
    return list(visible_text_paths(slide).values())
