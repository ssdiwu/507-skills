#!/usr/bin/env python3
"""Generate machine-verifiable browser evidence for one final-form HTML candidate."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from PIL import Image, ImageDraw
from websockets.sync.client import connect

from artifact_evidence import validate_artifact, validate_png
from browser_tools import chrome_version, find_chrome
from design_system import normalize_deck
from verification_report import digest, validate_report
from visual_plan import load_plan, text_flow_limits, validate_plan

ROOT = Path(__file__).resolve().parents[1]


class BrowserEvidenceError(RuntimeError):
    pass


class CdpSession:
    def __init__(self, chrome: Path, temporary: Path) -> None:
        self.profile = temporary / "chrome-profile"
        self.profile.mkdir()
        command = [
            str(chrome), "--headless=new", "--disable-gpu", "--disable-dev-shm-usage", "--no-first-run",
            "--no-default-browser-check", "--hide-scrollbars", "--remote-allow-origins=*", "--remote-debugging-port=0",
            f"--user-data-dir={self.profile}", "about:blank",
        ]
        self.process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        port_file = self.profile / "DevToolsActivePort"
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline and not port_file.is_file():
            if self.process.poll() is not None:
                stderr = self.process.stderr.read() if self.process.stderr else ""
                raise BrowserEvidenceError(f"Chrome stopped before DevTools became ready: {stderr[-1200:]}")
            time.sleep(0.05)
        if not port_file.is_file():
            raise BrowserEvidenceError("Chrome DevTools did not become ready")
        self.port = int(port_file.read_text(encoding="utf-8").splitlines()[0])
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/json/list", timeout=5) as response:
            targets = json.load(response)
        target = next((item for item in targets if item.get("type") == "page"), None)
        if target is None:
            raise BrowserEvidenceError("Chrome did not expose a page target")
        self.socket = connect(target["webSocketDebuggerUrl"], open_timeout=10, max_size=16 * 1024 * 1024)
        self.next_id = 0
        self.events: list[dict[str, Any]] = []
        self.javascript_enabled = True
        self.command("Page.enable")
        self.command("Runtime.enable")

    def command(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self.next_id += 1
        request_id = self.next_id
        self.socket.send(json.dumps({"id": request_id, "method": method, "params": params or {}}))
        while True:
            message = json.loads(self.socket.recv())
            if message.get("id") == request_id:
                if "error" in message:
                    raise BrowserEvidenceError(f"CDP {method} failed: {message['error']}")
                return message.get("result") or {}
            self.events.append(message)

    def wait_event(self, method: str, timeout: float = 15) -> dict[str, Any]:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            for index, event in enumerate(self.events):
                if event.get("method") == method:
                    return self.events.pop(index)
            remaining = max(0.1, deadline - time.monotonic())
            self.socket.socket.settimeout(remaining)
            try:
                event = json.loads(self.socket.recv())
            except TimeoutError as error:
                raise BrowserEvidenceError(f"timed out waiting for {method}") from error
            if event.get("method") == method:
                return event
            self.events.append(event)
        raise BrowserEvidenceError(f"timed out waiting for {method}")

    def evaluate(self, expression: str, *, await_promise: bool = False) -> Any:
        result = self.command("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": await_promise,
            "userGesture": True,
        })
        if result.get("exceptionDetails"):
            details = result["exceptionDetails"]
            raise BrowserEvidenceError(f"browser evaluation failed: {details.get('text') or details}")
        return (result.get("result") or {}).get("value")

    def set_viewport(self, width: int, height: int) -> None:
        self.command("Emulation.setDeviceMetricsOverride", {
            "width": width, "height": height, "deviceScaleFactor": 1, "mobile": width <= 480,
            "screenWidth": width, "screenHeight": height,
        })

    def set_reduced_motion(self, reduced: bool) -> None:
        features = [{"name": "prefers-reduced-motion", "value": "reduce" if reduced else "no-preference"}]
        self.command("Emulation.setEmulatedMedia", {"media": "screen", "features": features})

    def set_javascript(self, enabled: bool) -> None:
        self.command("Emulation.setScriptExecutionDisabled", {"value": not enabled})
        self.javascript_enabled = enabled

    def navigate(self, url: str) -> None:
        self.events.clear()
        self.command("Page.navigate", {"url": url})
        self.wait_event("Page.loadEventFired")
        if self.javascript_enabled and self.evaluate("typeof document.fonts !== 'undefined'"):
            self.evaluate("document.fonts.ready.then(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))))", await_promise=True)

    def screenshot(self, path: Path) -> None:
        result = self.command("Page.captureScreenshot", {"format": "png", "fromSurface": True, "captureBeyondViewport": False})
        path.write_bytes(base64.b64decode(result["data"]))
        validate_png(path, "browser screenshot")

    def close(self) -> None:
        try:
            self.socket.close()
        finally:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)


def url_for(artifact: Path, **params: object) -> str:
    query = urlencode({key: str(value) for key, value in params.items()})
    return artifact.resolve().as_uri() + (f"?{query}" if query else "")


def page_status(page: dict[str, Any], index: int, total: int, limits: dict[str, int], component: str) -> tuple[str, dict[str, Any]]:
    failures: list[str] = []
    if page.get("currentId") != page.get("id") or page.get("statusText") != f"{index + 1} / {total}":
        failures.append("current page mapping")
    if page.get("transitionMs") != 0 or abs(float(page.get("offsetErrorPx", 999))) > 1:
        failures.append("settled capture")
    if page.get("overflow") != "pass" or page.get("phraseOverflow"):
        failures.append("overflow")
    if component == "table" and page.get("tableBackground") != "none":
        failures.append("table background suppression")
    actual = page.get("textFlows") or {}
    flows: dict[str, Any] = {}
    for path, maximum in limits.items():
        lines = actual.get(path)
        passed = isinstance(lines, int) and 1 <= lines <= maximum
        flows[path] = {"lines": lines, "maxLines": maximum, "status": "passed" if passed else "failed"}
        if not passed:
            failures.append(f"textFlow {path}")
    page["textFlows"] = flows
    page["status"] = "passed" if not failures else "failed"
    return page["status"], {"page": page.get("id"), "failures": failures}


def contact_sheet(paths: list[Path], output: Path) -> None:
    thumbnails: list[Image.Image] = []
    for path in paths:
        with Image.open(path) as source:
            image = source.convert("RGB")
            image.thumbnail((480, 300))
            thumbnails.append(image.copy())
    columns = min(4, len(thumbnails))
    rows = (len(thumbnails) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * 500, rows * 330), "#11151b")
    draw = ImageDraw.Draw(sheet)
    for index, image in enumerate(thumbnails):
        x, y = (index % columns) * 500, (index // columns) * 330
        sheet.paste(image, (x + 10, y + 10))
        draw.text((x + 12, y + 312), f"{index + 1:02d}", fill="white")
    sheet.save(output, format="PNG")
    validate_png(output, "browser contact sheet")


def git_revision() -> tuple[str, str]:
    try:
        revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, text=True, capture_output=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, check=True, text=True, capture_output=True).stdout.strip())
        return revision, "dirty" if dirty else "clean"
    except (OSError, subprocess.CalledProcessError):
        return "unknown", "unknown"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--chrome")
    args = parser.parse_args()
    browser = find_chrome(args.chrome)
    if browser is None:
        raise SystemExit("Chrome/Chromium not found; set CHROME_PATH or install a compatible browser")
    try:
        validate_artifact(args.artifact, "html")
    except ValueError as error:
        raise SystemExit(str(error)) from error
    raw = json.loads(args.input.read_text(encoding="utf-8"))
    content = normalize_deck(raw)
    plan = load_plan(args.plan, raw)
    plan_errors = validate_plan(plan, raw, "html")
    if plan_errors:
        raise SystemExit("invalid visual plan: " + "; ".join(plan_errors))
    if args.output_dir.exists():
        raise SystemExit("output-dir already exists; browser evidence must be generated into a new directory")
    components = {slide["id"]: slide["component"] for slide in content["slides"]}
    limits = text_flow_limits(plan)
    failures: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix=f".{args.output_dir.name}-candidate-", dir=args.output_dir.parent) as temporary_name:
        temporary = Path(temporary_name)
        evidence = temporary / args.output_dir.name
        evidence.mkdir()
        session = CdpSession(browser, temporary)
        try:
            session.set_javascript(True)
            session.set_reduced_motion(False)
            session.set_viewport(1440, 900)
            session.navigate(url_for(args.artifact, instant=1, audit=1, slide=0))
            interaction_result = session.evaluate("""(()=>{const result={};go(0);next.click();result.button=index===1;go(0);dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowRight'}));result.keyboard=index===1;go(1);dispatchEvent(new WheelEvent('wheel',{deltaY:-100}));result.wheel=index===0;go(0);const start=new Event('touchstart');Object.defineProperty(start,'touches',{value:[{clientY:500}]});dispatchEvent(start);const end=new Event('touchend');Object.defineProperty(end,'changedTouches',{value:[{clientY:400}]});dispatchEvent(end);result.touch=index===1;prev.focus();result.focus=document.activeElement===prev;go(0);return result})()""")
            interaction_result["status"] = "passed" if all(interaction_result.values()) else "failed"
            pages: list[dict[str, Any]] = []
            screenshots: list[Path] = []
            for index, slide in enumerate(content["slides"]):
                snapshot = session.evaluate(f"go({index});fitPhrases();publishAudit();auditSnapshot()")
                screenshot = evidence / f"slide-{index + 1}.png"
                session.screenshot(screenshot)
                snapshot.update({
                    "id": slide["id"], "index": index, "settled": True, "text": session.evaluate("slides[index].innerText"),
                    "screenshot": screenshot.name, "screenshotSha256": digest(screenshot),
                })
                status, failure = page_status(snapshot, index, len(content["slides"]), limits.get(slide["id"], {}), slide["component"])
                if status != "passed":
                    failures.append(failure)
                pages.append(snapshot)
                screenshots.append(screenshot)
            session.set_viewport(390, 844)
            session.navigate(url_for(args.artifact, static=1, audit=1))
            mobile = session.evaluate("auditSnapshot()")
            mobile_profile = {"status": "passed" if mobile.get("overflow") == "pass" and mobile.get("responsive") == "pass" and not mobile.get("phraseOverflow") else "failed", "overflow": mobile.get("overflow"), "overflowSlides": mobile.get("overflowSlides"), "responsive": mobile.get("responsive"), "phraseOverflow": mobile.get("phraseOverflow")}
            session.set_viewport(1440, 900)
            session.set_reduced_motion(True)
            session.navigate(url_for(args.artifact, audit=1))
            reduced = session.evaluate("auditSnapshot()")
            reduced_profile = {"status": "passed" if reduced.get("motion") == "reduced" and reduced.get("transitionMs") == 0 and reduced.get("staticClass") is False else "failed", "motion": reduced.get("motion"), "transitionMs": reduced.get("transitionMs"), "staticClass": reduced.get("staticClass")}
            session.set_reduced_motion(False)
            failure_index = min(1, len(content["slides"]) - 1)
            session.navigate(url_for(args.artifact, **{"fail-after": 1, "audit": 1, "slide": failure_index}))
            session.evaluate("new Promise(resolve=>setTimeout(resolve,100))", await_promise=True)
            fallback = session.evaluate("auditSnapshot()")
            fallback_transform = session.evaluate("getComputedStyle(deck).transform")
            fallback_profile = {"status": "passed" if fallback.get("staticClass") is True and fallback.get("visible") == len(content["slides"]) and fallback_transform == "none" and fallback.get("currentId") == content["slides"][failure_index]["id"] else "failed", "staticClass": fallback.get("staticClass"), "visible": fallback.get("visible"), "deckTransform": fallback_transform, "currentId": fallback.get("currentId"), "statusText": fallback.get("statusText")}
            resize_slide = next((slide for slide in plan["slides"] if any((spec or {}).get("preferSingleLine") for spec in (slide.get("textFlow") or {}).values())), plan["slides"][0])
            resize_index = next(index for index, slide in enumerate(plan["slides"]) if slide["id"] == resize_slide["id"])
            resize_path = next(iter(resize_slide.get("textFlow") or {}), None)
            session.set_viewport(700, 900)
            session.navigate(url_for(args.artifact, instant=1, audit=1, slide=resize_index))
            narrow = session.evaluate("auditSnapshot()")
            session.set_viewport(1440, 900)
            session.evaluate("new Promise(resolve=>requestAnimationFrame(()=>{fitPhrases();publishAudit();resolve()}))", await_promise=True)
            wide = session.evaluate("auditSnapshot()")
            narrow_lines = (narrow.get("textFlows") or {}).get(resize_path, 1) if resize_path else 1
            wide_lines = (wide.get("textFlows") or {}).get(resize_path, 1) if resize_path else 1
            resize_profile = {"status": "passed" if wide_lines <= max(1, narrow_lines) else "failed", "path": resize_path, "narrowLines": narrow_lines, "wideLines": wide_lines}
            session.set_javascript(False)
            session.navigate(url_for(args.artifact))
            first_slide = content["slides"][0]
            visible_anchor = json.dumps(str(first_slide.get("title") or first_slide.get("quote") or first_slide["id"]), ensure_ascii=False)
            no_javascript = session.evaluate(f"(()=>{{const slides=[...document.querySelectorAll('.slide')];return{{visible:slides.filter(slide=>getComputedStyle(slide).display!=='none').length,scrollHeight:document.documentElement.scrollHeight,viewport:innerHeight,pagesHaveViewportHeight:slides.every(slide=>slide.getBoundingClientRect().height>=innerHeight-1),containsTitle:document.body.innerText.includes({visible_anchor})}}}})()")
            no_javascript_screenshot = evidence / "no-javascript.png"
            session.screenshot(no_javascript_screenshot)
            no_javascript_profile = {"status": "passed" if no_javascript.get("visible") == len(content["slides"]) and no_javascript.get("scrollHeight", 0) >= no_javascript.get("viewport", 1) * len(content["slides"]) and no_javascript.get("pagesHaveViewportHeight") is True and no_javascript.get("containsTitle") is True else "failed", **no_javascript, "screenshot": no_javascript_screenshot.name, "screenshotSha256": digest(no_javascript_screenshot)}
        finally:
            session.close()
        profiles = {
            "desktop": {"status": "passed" if not failures else "failed"},
            "mobile": mobile_profile,
            "reducedMotion": reduced_profile,
            "failureFallback": fallback_profile,
            "resizeRecovery": resize_profile,
            "noJavaScript": no_javascript_profile,
            "interactions": interaction_result,
        }
        for name, profile in profiles.items():
            if profile.get("status") != "passed":
                failures.append({"profile": name, "values": profile})
        contact_sheet(screenshots, evidence / "contact-sheet.png")
        revision, worktree_status = git_revision()
        report = {
            "version": 1,
            "kind": "html-browser",
            "status": "passed" if not failures else "failed",
            "failures": failures,
            "producer": {
                "name": "html_browser_evidence.py",
                "sourceSha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "browser": browser.name,
                "browserVersion": chrome_version(browser),
                "generatedAt": datetime.now(timezone.utc).isoformat(),
                "gitRevision": revision,
                "worktreeStatus": worktree_status,
            },
            "subject": {
                "inputId": content["id"], "inputSha256": digest(args.input), "visualPlanSha256": digest(args.plan),
                "artifactSha256": digest(args.artifact), "carrier": "html",
            },
            "checks": [
                {"name": "all-pages-settled", "status": "passed" if not any("page" in item for item in failures) else "failed"},
                {"name": "responsive-fallback-and-interactions", "status": "passed" if all(profile.get("status") == "passed" for profile in profiles.values()) else "failed"},
            ],
            "profiles": profiles,
            "pages": pages,
        }
        report_path = evidence / "browser-report.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if failures:
            raise SystemExit("HTML browser evidence failed: " + json.dumps(failures, ensure_ascii=False))
        expected_subject = report["subject"]
        try:
            validate_report(report_path, expected_subject, [slide["id"] for slide in content["slides"]], limits, components)
        except ValueError as error:
            raise SystemExit(str(error)) from error
        os.replace(evidence, args.output_dir)
    print(f"HTML browser evidence passed: {args.output_dir}")


if __name__ == "__main__":
    main()
