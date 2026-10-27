"""Machine-verifiable evidence report contract for 507-ppt manifest v2."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from artifact_evidence import validate_png


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_report(
    path: Path,
    expected_subject: dict[str, str],
    page_ids: list[str],
    text_flow_limits: dict[str, dict[str, int]] | None = None,
    components: dict[str, str] | None = None,
    expected_pictures: int | None = None,
) -> dict[str, Any]:
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"verification report is unreadable: {path}") from error
    if report.get("version") != 1 or not isinstance(report.get("kind"), str):
        raise ValueError(f"verification report contract is invalid: {path}")
    if report.get("status") != "passed" or report.get("failures") not in (None, []):
        raise ValueError(f"verification report did not pass: {path}")
    subject = report.get("subject")
    if not isinstance(subject, dict) or any(subject.get(key) != value for key, value in expected_subject.items()):
        raise ValueError(f"verification report subject mismatch: {path}")
    checks = report.get("checks")
    if not isinstance(checks, list) or not checks or any(not isinstance(item, dict) or item.get("status") != "passed" for item in checks):
        raise ValueError(f"verification report checks are incomplete or failed: {path}")
    producer = report.get("producer")
    required_producer = ("name", "sourceSha256", "generatedAt", "gitRevision")
    if not isinstance(producer, dict) or any(not producer.get(key) for key in required_producer):
        raise ValueError(f"verification report producer metadata is incomplete: {path}")
    producer_path = Path(__file__).with_name(str(producer["name"]))
    if not producer_path.is_file() or digest(producer_path) != producer["sourceSha256"]:
        raise ValueError(f"verification report producer source hash is stale: {path}")
    try:
        datetime.fromisoformat(str(producer["generatedAt"]).replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"verification report generatedAt is invalid: {path}") from error
    if report["kind"] == "html-browser":
        if any(not producer.get(key) for key in ("browser", "browserVersion")):
            raise ValueError(f"HTML browser report producer metadata is incomplete: {path}")
        profiles = report.get("profiles")
        required_profiles = ("desktop", "mobile", "reducedMotion", "failureFallback", "resizeRecovery", "noJavaScript", "interactions")
        if not isinstance(profiles, dict) or any((profiles.get(name) or {}).get("status") != "passed" for name in required_profiles):
            raise ValueError(f"HTML browser profiles are incomplete or failed: {path}")
        mobile = profiles["mobile"]
        reduced = profiles["reducedMotion"]
        fallback = profiles["failureFallback"]
        resize = profiles["resizeRecovery"]
        no_javascript = profiles["noJavaScript"]
        interactions = profiles["interactions"]
        if mobile.get("overflow") != "pass" or mobile.get("responsive") != "pass" or mobile.get("phraseOverflow") not in (None, []):
            raise ValueError(f"HTML mobile profile fields failed: {path}")
        if reduced.get("motion") != "reduced" or reduced.get("transitionMs") != 0 or reduced.get("staticClass") is not False:
            raise ValueError(f"HTML reduced-motion profile fields failed: {path}")
        if fallback.get("staticClass") is not True or fallback.get("visible") != len(page_ids) or fallback.get("deckTransform") != "none" or fallback.get("currentId") != page_ids[min(1, len(page_ids) - 1)] or fallback.get("statusText") != f"{min(1, len(page_ids) - 1) + 1} / {len(page_ids)}":
            raise ValueError(f"HTML failure fallback fields failed: {path}")
        if resize.get("wideLines", 999) > max(1, resize.get("narrowLines", 0)):
            raise ValueError(f"HTML resize recovery fields failed: {path}")
        no_javascript_relative = Path(str(no_javascript.get("screenshot") or ""))
        no_javascript_screenshot = (path.parent / no_javascript_relative).resolve()
        if no_javascript_relative.is_absolute() or path.parent.resolve() not in no_javascript_screenshot.parents or no_javascript.get("visible") != len(page_ids) or no_javascript.get("scrollHeight", 0) < no_javascript.get("viewport", 1) * len(page_ids) or no_javascript.get("pagesHaveViewportHeight") is not True or no_javascript.get("containsTitle") is not True or not no_javascript_screenshot.is_file() or digest(no_javascript_screenshot) != no_javascript.get("screenshotSha256"):
            raise ValueError(f"HTML no-JavaScript profile fields failed: {path}")
        try:
            validate_png(no_javascript_screenshot, "HTML no-JavaScript screenshot")
        except ValueError as error:
            raise ValueError(str(error)) from error
        if any(interactions.get(name) is not True for name in ("button", "keyboard", "wheel", "touch", "focus")):
            raise ValueError(f"HTML interaction profile fields failed: {path}")
        pages = report.get("pages")
        if not isinstance(pages, list) or [item.get("id") for item in pages if isinstance(item, dict)] != page_ids:
            raise ValueError(f"HTML browser page mapping mismatch: {path}")
        for index, page in enumerate(pages, start=1):
            screenshot_value = str(page.get("screenshot") or "")
            screenshot_relative = Path(screenshot_value)
            screenshot = (path.parent / screenshot_relative).resolve()
            if screenshot_relative.is_absolute() or path.parent.resolve() not in screenshot.parents:
                raise ValueError(f"HTML browser screenshot path escapes evidence directory: {path} page {index}")
            if (
                page.get("status") != "passed"
                or page.get("currentId") != page.get("id")
                or page.get("statusText") != f"{index} / {len(page_ids)}"
                or page.get("settled") is not True
                or page.get("transitionMs") != 0
                or abs(float(page.get("offsetErrorPx", 999))) > 1
                or page.get("overflow") != "pass"
                or page.get("phraseOverflow") not in (None, [])
                or not screenshot.is_file()
                or digest(screenshot) != page.get("screenshotSha256")
            ):
                raise ValueError(f"HTML browser page evidence failed: {path} page {index}")
            try:
                validate_png(screenshot, f"HTML browser page {index} screenshot")
            except ValueError as error:
                raise ValueError(str(error)) from error
            if (components or {}).get(page["id"]) == "table" and page.get("tableBackground") != "none":
                raise ValueError(f"HTML table background suppression failed: {path} page {index}")
            expected_flows = (text_flow_limits or {}).get(page["id"], {})
            actual_flows = page.get("textFlows") or {}
            if set(actual_flows) != set(expected_flows):
                raise ValueError(f"HTML browser text-flow mapping mismatch: {path} page {index}")
            for text_path, max_lines in expected_flows.items():
                flow = actual_flows[text_path]
                if flow.get("status") != "passed" or flow.get("maxLines") != max_lines or not isinstance(flow.get("lines"), int) or not 1 <= flow["lines"] <= max_lines:
                    raise ValueError(f"HTML browser text-flow lines failed: {path} page {index} {text_path}")
    elif report["kind"] == "axis-content" and expected_subject.get("carrier") == "pptx":
        evidence = report.get("carrierEvidence") or {}
        expected_charts = sum(component == "chart" for component in (components or {}).values())
        expected_tables = sum(component == "table" for component in (components or {}).values())
        if (
            producer.get("tool") != "officecli"
            or not producer.get("toolVersion")
            or evidence.get("schema") != "passed"
            or evidence.get("issues") != 0
            or evidence.get("alt") != "passed"
            or evidence.get("nativeCharts") != expected_charts
            or evidence.get("nativeTables") != expected_tables
            or (expected_pictures is not None and evidence.get("nativePictures") != expected_pictures)
            or evidence.get("screenshots") != len(page_ids)
        ):
            raise ValueError(f"PPTX axis-content producer or carrier evidence is incomplete: {path}")
    return report
