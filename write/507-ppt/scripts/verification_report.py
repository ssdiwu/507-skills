"""Machine-verifiable evidence report contract for 507-ppt manifest v2."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_report(path: Path, expected_subject: dict[str, str], page_ids: list[str], text_flow_limits: dict[str, dict[str, int]] | None = None) -> dict[str, Any]:
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
    if report["kind"] == "html-browser":
        profiles = report.get("profiles")
        if not isinstance(profiles, dict) or any((profiles.get(name) or {}).get("status") != "passed" for name in ("desktop", "mobile", "reducedMotion", "failureFallback", "resizeRecovery")):
            raise ValueError(f"HTML browser profiles are incomplete or failed: {path}")
        mobile = profiles["mobile"]
        reduced = profiles["reducedMotion"]
        fallback = profiles["failureFallback"]
        resize = profiles["resizeRecovery"]
        if mobile.get("overflow") != "pass" or mobile.get("responsive") != "pass" or mobile.get("phraseOverflow") not in (None, []):
            raise ValueError(f"HTML mobile profile fields failed: {path}")
        if reduced.get("motion") != "reduced" or reduced.get("hero") != "none" or reduced.get("transitionMs") != 0:
            raise ValueError(f"HTML reduced-motion profile fields failed: {path}")
        if fallback.get("staticClass") is not True or fallback.get("visible") != len(page_ids):
            raise ValueError(f"HTML failure fallback fields failed: {path}")
        if resize.get("wideLines", 999) > max(1, resize.get("narrowLines", 0)):
            raise ValueError(f"HTML resize recovery fields failed: {path}")
        pages = report.get("pages")
        if not isinstance(pages, list) or [item.get("id") for item in pages if isinstance(item, dict)] != page_ids:
            raise ValueError(f"HTML browser page mapping mismatch: {path}")
        for index, page in enumerate(pages, start=1):
            screenshot = path.parent / str(page.get("screenshot") or "")
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
            expected_flows = (text_flow_limits or {}).get(page["id"], {})
            actual_flows = page.get("textFlows") or {}
            if set(actual_flows) != set(expected_flows):
                raise ValueError(f"HTML browser text-flow mapping mismatch: {path} page {index}")
            for text_path, max_lines in expected_flows.items():
                flow = actual_flows[text_path]
                if flow.get("status") != "passed" or flow.get("maxLines") != max_lines or not isinstance(flow.get("lines"), int) or flow["lines"] > max_lines:
                    raise ValueError(f"HTML browser text-flow lines failed: {path} page {index} {text_path}")
    return report
