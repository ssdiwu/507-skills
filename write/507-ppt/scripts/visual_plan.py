"""Visual-plan contract and compatibility resolution for 507-ppt."""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from artifact_evidence import validate_artifact, validate_png
from design_system import COMPONENTS, PRESETS, TREATMENTS, normalize_deck, preferred_presentation, preset, resolve_combination, visible_strings, visible_text_paths
from text_layout import validate_text_flow

ROOT = Path(__file__).resolve().parents[1]
PLAN_FIELDS = {"version", "inputId", "inputSha256", "targets", "preset", "language", "prototype", "slides"}
LANGUAGE_FIELDS = {"id", "variant"}
SLIDE_FIELDS = {"id", "presentation", "treatment", "textFlow", "reason"}


def content_sha256(data: dict[str, Any]) -> str:
    payload = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def text_at(slide: dict[str, Any], path: str) -> str | None:
    return visible_text_paths(slide).get(path)


def plan_for_preset(data: dict[str, Any], preset_name: str = "swiss", *, prototype_status: str = "skipped", skip_reason: str = "explicit validated preset") -> dict[str, Any]:
    normalized = normalize_deck(data)
    selected = preset(preset_name)
    return {
        "version": 1,
        "inputId": normalized.get("id"),
        "inputSha256": content_sha256(normalized),
        "targets": ["html", "pptx"],
        "preset": preset_name,
        "language": {"id": selected["language"], "variant": selected["variant"]},
        "prototype": {"mode": "adaptive", "status": prototype_status, "skipReason": skip_reason} if prototype_status == "skipped" else {"mode": "adaptive", "status": prototype_status},
        "slides": [
            {"id": slide["id"], "presentation": preferred_presentation(slide["component"]), "treatment": "default", "textFlow": {}}
            for slide in normalized.get("slides") or []
        ],
    }


PROTOTYPE_RECIPES: dict[str, dict[str, Any]] = {
    "swiss": {
        "rationale": "优先显示严谨层级、关系结构与数据证据。",
        "presentations": {},
    },
    "cobalt": {
        "rationale": "用面板分组与产品界面框架增强模块感和可操作感。",
        "presentations": {
            "cover": "panel-led", "section": "panel-led", "closing": "panel-led", "statement": "panel-led",
            "collection": "panel-led", "comparison": "panel-led", "sequence": "panel-led", "relationship": "panel-led",
            "media-evidence": "ui-product-led", "metric": "panel-led", "chart": "panel-led", "table": "panel-led",
        },
    },
    "magazine": {
        "rationale": "用编辑规则、印刷节奏与素材主导建立叙事层次。",
        "presentations": {
            "cover": "editorial-print-led", "section": "editorial-print-led", "closing": "editorial-print-led", "statement": "editorial-print-led",
            "collection": "editorial-print-led", "comparison": "editorial-print-led", "sequence": "hand-drawn-explainer",
            "relationship": "hand-drawn-explainer", "media-evidence": "photo-led", "quote": "editorial-print-led",
            "metric": "type-led", "chart": "editorial-print-led", "table": "editorial-print-led",
        },
    },
    "clay": {
        "rationale": "用温暖叙事、素材主角与柔和关系图承载案例。",
        "presentations": {"cover": "editorial-print-led", "relationship": "hand-drawn-explainer", "media-evidence": "photo-led"},
    },
    "forest": {
        "rationale": "优先研究型关系、数据与低装饰证据表达。",
        "presentations": {"relationship": "schematic-led", "media-evidence": "photo-led", "metric": "data-led", "chart": "data-led", "table": "data-led"},
    },
    "noir": {
        "rationale": "用强声明与示意关系形成高对比、低装饰表达。",
        "presentations": {"cover": "type-led", "statement": "type-led", "collection": "schematic-led", "comparison": "schematic-led", "sequence": "schematic-led", "relationship": "schematic-led"},
    },
}


def plan_for_prototype_candidate(data: dict[str, Any], preset_name: str, candidate_id: str, representative_ids: list[str]) -> dict[str, Any]:
    plan = plan_for_preset(data, preset_name, prototype_status="candidate")
    recipe = PROTOTYPE_RECIPES[preset_name]
    by_component = recipe["presentations"]
    normalized = normalize_deck(data)
    for slide, visual in zip(normalized["slides"], plan["slides"], strict=True):
        presentation = by_component.get(slide["component"])
        if presentation in COMPONENTS[slide["component"]]["presentations"]:
            visual["presentation"] = presentation
        if slide["component"] == "table":
            visual["treatment"] = "dense"
        if COMPONENTS[slide["component"]]["presentations"].get(visual["presentation"]) == "conditional":
            visual["reason"] = "prototype explores a conditionally compatible presentation with real content"
    plan["prototype"].update({
        "candidateId": candidate_id,
        "representativeSlides": representative_ids,
        "rationale": recipe["rationale"],
    })
    return plan


def load_plan(path: Path | None, data: dict[str, Any], preset_name: str | None = None) -> dict[str, Any]:
    if path is None:
        if data.get("version") == 3 and preset_name is None:
            raise ValueError("content v3 requires --plan or an explicit --preset")
        return plan_for_preset(data, preset_name or "swiss", skip_reason="explicit validated preset" if preset_name else "legacy default preset compatibility")
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_prototype(prototype: Any, *, allow_candidate: bool = False) -> list[str]:
    if not isinstance(prototype, dict):
        return ["prototype contract missing"]
    status = prototype.get("status")
    allowed = ("approved", "skipped", "candidate") if allow_candidate else ("approved", "skipped")
    if status not in allowed:
        return ["prototype status must be approved or skipped" + (" or candidate" if allow_candidate else "")]
    if status == "skipped" and not prototype.get("skipReason"):
        return ["skipped prototype requires skipReason"]
    if status == "approved":
        required = ("manifest", "manifestSha256", "representativeSlides", "candidates", "selectedCandidate")
        if any(not prototype.get(key) for key in required):
            return ["approved prototype requires bound manifest, hash, representative slides, candidates, and selected candidate"]
        candidates = prototype.get("candidates")
        if not isinstance(candidates, list) or not 2 <= len(candidates) <= 3:
            return ["approved prototype requires 2-3 candidates"]
        candidate_ids = [item.get("id") for item in candidates if isinstance(item, dict)]
        if prototype.get("selectedCandidate") not in candidate_ids:
            return ["approved prototype selectedCandidate must exist in candidates"]
    mixed = prototype.get("mixedFrom") or []
    if mixed:
        candidates = prototype.get("candidates") or []
        candidate_ids = [item.get("id") for item in candidates if isinstance(item, dict)]
        if not isinstance(mixed, list) or not 2 <= len(mixed) <= 3 or len(set(mixed)) != len(mixed) or not set(mixed).issubset(set(candidate_ids)):
            return ["mixed prototype requires 2-3 distinct existing candidate ids"]
        merged = prototype.get("mergedPrototype")
        required_merged = ("artifact", "artifactSha256", "visualPlan", "visualPlanSha256", "evidence", "evidenceSha256")
        if not isinstance(merged, dict) or any(not merged.get(key) for key in required_merged):
            return ["mixed prototype requires bound merged artifact, visual plan, evidence, and hashes"]
    return []


def _prototype_manifest(prototype: dict[str, Any]) -> tuple[dict[str, Any] | None, Path | None, list[str]]:
    value = prototype.get("manifest")
    expected_hash = prototype.get("manifestSha256")
    if not isinstance(value, str) or not value or not isinstance(expected_hash, str):
        return None, None, ["approved prototype manifest binding is incomplete"]
    path = (ROOT / value).resolve()
    if ROOT != path and ROOT not in path.parents:
        return None, None, ["approved prototype manifest path escapes skill root"]
    if not path.is_file():
        return None, path, ["approved prototype manifest file is missing"]
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
        return None, path, ["approved prototype manifest hash mismatch"]
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None, path, ["approved prototype manifest is unreadable"]
    return manifest, path, []


def _bound_prototype_file(root: Path, value: Any, expected_hash: Any, label: str) -> tuple[Path | None, list[str]]:
    if not isinstance(value, str) or not value or not isinstance(expected_hash, str):
        return None, [f"{label} binding is incomplete"]
    relative = Path(value)
    path = (root / relative).resolve()
    if relative.is_absolute() or root.resolve() not in path.parents:
        return None, [f"{label} path escapes prototype package"]
    if not path.is_file():
        return path, [f"{label} is missing"]
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
        return path, [f"{label} hash mismatch"]
    return path, []


def validate_plan(plan: Any, data: dict[str, Any], carrier: str | None = None, *, allow_candidate: bool = False) -> list[str]:
    normalized = normalize_deck(data)
    if not isinstance(plan, dict) or plan.get("version") != 1:
        return ["visual plan version must be 1"]
    errors: list[str] = []
    extra_plan = sorted(set(plan) - PLAN_FIELDS)
    if extra_plan:
        errors.append("unsupported visual-plan field(s): " + ", ".join(extra_plan))
    if plan.get("inputId") != normalized.get("id"):
        errors.append("visual plan inputId mismatch")
    if plan.get("inputSha256") and plan.get("inputSha256") != content_sha256(normalized):
        errors.append("visual plan input hash mismatch")
    language_block = plan.get("language")
    if not isinstance(language_block, dict) or not language_block.get("id"):
        errors.append("visual plan language missing")
        language_id = ""
    else:
        language_id = language_block["id"]
        extra_language = sorted(set(language_block) - LANGUAGE_FIELDS)
        if extra_language:
            errors.append("unsupported visual-plan language field(s): " + ", ".join(extra_language))
    errors.extend(_validate_prototype(plan.get("prototype"), allow_candidate=allow_candidate))
    plan_slides = plan.get("slides")
    if not isinstance(plan_slides, list):
        return errors + ["visual plan slides must be a list"]
    if [item.get("id") for item in plan_slides if isinstance(item, dict)] != [slide["id"] for slide in normalized.get("slides") or []]:
        errors.append("visual plan slide order must match content")
        return errors
    targets = [carrier] if carrier else plan.get("targets") or ["html", "pptx"]
    representative_ids = (plan.get("prototype") or {}).get("representativeSlides") or []
    if representative_ids and (not isinstance(representative_ids, list) or not 1 <= len(representative_ids) <= 3 or not set(representative_ids).issubset({slide["id"] for slide in normalized["slides"]})):
        errors.append("prototype representativeSlides must contain 1-3 existing slide ids")
    prototype = plan.get("prototype") or {}
    if prototype.get("status") == "approved" and not any("approved prototype" in error for error in errors):
        prototype_manifest, prototype_path, prototype_errors = _prototype_manifest(prototype)
        errors.extend(prototype_errors)
        if prototype_manifest is not None and prototype_path is not None:
            if prototype_manifest.get("status") != "approved" or prototype_manifest.get("inputId") != normalized.get("id"):
                errors.append("approved prototype manifest status or inputId mismatch")
            if prototype_manifest.get("representativeSlides") != representative_ids:
                errors.append("approved prototype representativeSlides differ from manifest")
            if prototype_manifest.get("selectedCandidate") != prototype.get("selectedCandidate"):
                errors.append("approved prototype selectedCandidate differs from manifest")
            manifest_candidates = prototype_manifest.get("candidates") or []
            if [item.get("id") for item in manifest_candidates] != [item.get("id") for item in prototype.get("candidates") or []]:
                errors.append("approved prototype candidate ids differ from manifest")
            selected = next((item for item in manifest_candidates if item.get("id") == prototype.get("selectedCandidate")), None)
            reference_plan: dict[str, Any] | None = None
            if selected is None:
                errors.append("approved prototype selected candidate is absent from manifest")
            else:
                selected_artifact_path = prototype_path.parent / str(selected.get("artifact") or "")
                if not selected_artifact_path.is_file() or hashlib.sha256(selected_artifact_path.read_bytes()).hexdigest() != selected.get("artifactSha256"):
                    errors.append("approved prototype selected artifact is missing or stale")
                else:
                    try:
                        validate_artifact(selected_artifact_path, "html")
                    except ValueError as error:
                        errors.append(str(error))
                selected_plan_path = prototype_path.parent / str(selected.get("visualPlan") or "")
                if not selected_plan_path.is_file() or hashlib.sha256(selected_plan_path.read_bytes()).hexdigest() != selected.get("visualPlanSha256"):
                    errors.append("approved prototype selected visual plan is missing or stale")
                else:
                    selected_plan = json.loads(selected_plan_path.read_text(encoding="utf-8"))
                    reference_plan = selected_plan
            mixed = prototype.get("mixedFrom") or []
            if mixed:
                merged = prototype.get("mergedPrototype") or {}
                if prototype_manifest.get("mixedFrom") != mixed or prototype_manifest.get("mergedPrototype") != merged:
                    errors.append("approved merged prototype differs from manifest")
                merged_artifact, merged_errors = _bound_prototype_file(prototype_path.parent, merged.get("artifact"), merged.get("artifactSha256"), "approved merged prototype artifact")
                errors.extend(merged_errors)
                if merged_artifact is not None and not merged_errors:
                    try:
                        validate_artifact(merged_artifact, "html")
                    except ValueError as error:
                        errors.append(str(error))
                merged_plan_path, merged_plan_errors = _bound_prototype_file(prototype_path.parent, merged.get("visualPlan"), merged.get("visualPlanSha256"), "approved merged prototype visual plan")
                errors.extend(merged_plan_errors)
                merged_evidence, merged_evidence_errors = _bound_prototype_file(prototype_path.parent, merged.get("evidence"), merged.get("evidenceSha256"), "approved merged prototype evidence")
                errors.extend(merged_evidence_errors)
                if merged_evidence is not None and not merged_evidence_errors:
                    try:
                        validate_png(merged_evidence, "approved merged prototype evidence")
                    except ValueError as error:
                        errors.append(str(error))
                if merged_plan_path is not None and not merged_plan_errors:
                    try:
                        reference_plan = json.loads(merged_plan_path.read_text(encoding="utf-8"))
                    except (OSError, json.JSONDecodeError):
                        errors.append("approved merged prototype visual plan is unreadable")
            if reference_plan is not None:
                if reference_plan.get("language") != plan.get("language"):
                    errors.append("approved prototype language differs from final plan")
                reference_visuals = {item.get("id"): item for item in reference_plan.get("slides") or []}
                final_visuals = {item.get("id"): item for item in plan_slides}
                for slide_id in representative_ids:
                    reference_visual = reference_visuals.get(slide_id) or {}
                    final_visual = final_visuals.get(slide_id) or {}
                    if (reference_visual.get("presentation"), reference_visual.get("treatment", "default")) != (final_visual.get("presentation"), final_visual.get("treatment", "default")):
                        errors.append(f"approved prototype representative slide differs from final plan: {slide_id}")
            contact_sheet = prototype_path.parent / str(prototype_manifest.get("evidence") or "")
            if not contact_sheet.is_file() or hashlib.sha256(contact_sheet.read_bytes()).hexdigest() != prototype_manifest.get("evidenceSha256"):
                errors.append("approved prototype contact-sheet evidence is missing or stale")
            else:
                try:
                    validate_png(contact_sheet, "approved prototype contact-sheet evidence")
                except ValueError as error:
                    errors.append(str(error))
            target_evidence = prototype_manifest.get("targetEvidence") or {}
            for target in plan.get("targets") or []:
                evidence = target_evidence.get(target)
                if not isinstance(evidence, dict):
                    errors.append(f"approved prototype lacks {target} target evidence")
                    continue
                artifact_path = prototype_path.parent / str(evidence.get("artifact") or "")
                target_plan_path = prototype_path.parent / str(evidence.get("visualPlan") or "")
                if not artifact_path.is_file() or hashlib.sha256(artifact_path.read_bytes()).hexdigest() != evidence.get("artifactSha256"):
                    errors.append(f"approved prototype {target} artifact is missing or stale")
                else:
                    try:
                        validate_artifact(artifact_path, target)
                    except ValueError as error:
                        errors.append(str(error))
                if not target_plan_path.is_file() or hashlib.sha256(target_plan_path.read_bytes()).hexdigest() != evidence.get("visualPlanSha256"):
                    errors.append(f"approved prototype {target} plan is missing or stale")
                if mixed:
                    merged = prototype.get("mergedPrototype") or {}
                    if evidence.get("visualPlan") != merged.get("visualPlan") or evidence.get("visualPlanSha256") != merged.get("visualPlanSha256"):
                        errors.append(f"approved mixed prototype {target} evidence must use merged visual plan")
                if target == "pptx":
                    screenshots = evidence.get("screenshots") or []
                    if len(screenshots) != len(representative_ids):
                        errors.append("approved prototype PPTX screenshots do not match representative slides")
                    for screenshot in screenshots:
                        screenshot_path = prototype_path.parent / str(screenshot.get("path") or "")
                        if not screenshot_path.is_file() or hashlib.sha256(screenshot_path.read_bytes()).hexdigest() != screenshot.get("sha256"):
                            errors.append("approved prototype PPTX screenshot is missing or stale")
                        else:
                            try:
                                validate_png(screenshot_path, "approved prototype PPTX screenshot")
                            except ValueError as error:
                                errors.append(str(error))
    for slide, visual in zip(normalized["slides"], plan_slides, strict=True):
        if not isinstance(visual, dict):
            errors.append(f"visual plan entry for {slide['id']} must be an object")
            continue
        extra_visual = sorted(set(visual) - SLIDE_FIELDS)
        if extra_visual:
            errors.append(f"slide {slide['id']} unsupported visual-plan field(s): " + ", ".join(extra_visual))
        presentation = visual.get("presentation")
        treatment = visual.get("treatment", "default")
        if treatment not in TREATMENTS:
            errors.append(f"slide {slide['id']} has unknown treatment {treatment}")
        text_flow = visual.get("textFlow") or {}
        if not isinstance(text_flow, dict):
            errors.append(f"slide {slide['id']} textFlow must be an object")
            text_flow = {}
        for path, spec in text_flow.items():
            value = text_at(slide, path)
            if value is None:
                errors.append(f"slide {slide['id']} textFlow path not found: {path}")
                continue
            errors.extend(f"slide {slide['id']} {path}: {message}" for message in validate_text_flow(value, spec))
        for target in targets:
            try:
                resolved = resolve_combination(slide["component"], presentation, language_id, target, slide)
                if resolved["compatibility"] == "conditional" and not visual.get("reason"):
                    errors.append(f"slide {slide['id']} conditional presentation requires reason")
            except ValueError as error:
                errors.append(f"slide {slide['id']} ({target}): {error}")
    return errors


def resolved_pages(plan: dict[str, Any], data: dict[str, Any], carrier: str, *, allow_candidate: bool = False) -> list[dict[str, Any]]:
    normalized = normalize_deck(data)
    errors = validate_plan(plan, normalized, carrier, allow_candidate=allow_candidate)
    if errors:
        raise ValueError("invalid visual plan:\n- " + "\n- ".join(errors))
    language_id = plan["language"]["id"]
    result: list[dict[str, Any]] = []
    for slide, visual in zip(normalized["slides"], plan["slides"], strict=True):
        item = deepcopy(visual)
        item.update(resolve_combination(slide["component"], item["presentation"], language_id, carrier, slide))
        result.append(item)
    return result


def resolved_manifest_pages(plan: dict[str, Any], data: dict[str, Any], carrier: str) -> list[dict[str, Any]]:
    normalized = normalize_deck(data)
    resolved = resolved_pages(plan, normalized, carrier)
    return [
        {
            "id": slide["id"],
            "component": slide["component"],
            "presentation": visual["presentation"],
            "treatment": visual.get("treatment", "default"),
            "carrierSupport": visual["carrierSupport"],
            "suppressedDecorations": visual.get("suppressions") or [],
        }
        for slide, visual in zip(normalized["slides"], resolved, strict=True)
    ]


def expected_degradations(plan: dict[str, Any], data: dict[str, Any], carrier: str) -> list[dict[str, str]]:
    return [
        {"pageId": page["id"], "reason": f"{page['presentation']} uses carrier-adapted editable primitives"}
        for page in resolved_manifest_pages(plan, data, carrier)
        if page["carrierSupport"] == "adapted"
    ]


def text_flow_limits(plan: dict[str, Any]) -> dict[str, dict[str, int]]:
    return {
        slide["id"]: {path: spec["maxLines"] for path, spec in (slide.get("textFlow") or {}).items() if isinstance(spec, dict) and isinstance(spec.get("maxLines"), int)}
        for slide in plan.get("slides") or []
    }


def representative_slide_ids(data: dict[str, Any]) -> list[str]:
    normalized = normalize_deck(data)
    slides = normalized["slides"]
    chosen: list[str] = []
    cover = next((slide for slide in slides if slide["component"] == "cover"), slides[0])
    chosen.append(cover["id"])
    dense = max(slides, key=lambda slide: sum(len(value) for value in visible_strings(slide)))
    if dense["id"] not in chosen:
        chosen.append(dense["id"])
    evidence = next((slide for slide in slides if slide["component"] in {"metric", "chart", "table", "media-evidence"}), None)
    if evidence and evidence["id"] not in chosen:
        chosen.append(evidence["id"])
    return chosen[:3]


def candidate_presets(data: dict[str, Any]) -> list[str]:
    normalized = normalize_deck(data)
    scene = str(normalized.get("deck", {}).get("scene") or "").lower()
    components = {slide["component"] for slide in normalized["slides"]}
    if components & {"chart", "table", "relationship"} or any(word in scene for word in ("产品", "分析", "研究", "报告")):
        return ["swiss", "cobalt", "magazine"]
    if any(word in scene for word in ("品牌", "叙事", "文化", "设计")):
        return ["magazine", "clay", "noir"]
    return ["swiss", "magazine", "cobalt"]
