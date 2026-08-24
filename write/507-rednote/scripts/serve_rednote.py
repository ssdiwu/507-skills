#!/usr/bin/env python3
"""Serve the local 507-rednote workbench and export its compiled DOM pages."""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import io
import json
import mimetypes
import os
import secrets
import shutil
import signal
import subprocess
import tempfile
import threading
import time
import urllib.parse
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from PIL import Image

from render_rednote import build_contact_sheet, find_chrome


RUNTIME_VERSION = "0.1.0"
MAX_BODY_BYTES = 16 * 1024 * 1024
MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_IMAGE_PIXELS = 64_000_000
MANAGED_EXPORTS = ("pages", "contact-sheet.jpg", "rednote.pdf", "rednote.html", "render-manifest.json")
FONT_ASSETS = {
    "fonts/OFL-Source-Han-Sans.txt": "fcac737e761ec63dbfbdce11030a1780161920d80315edba9c8beff1c2bac5a2",
    "fonts/OFL-Source-Han-Serif.txt": "9ff5bb567e1b92c801fc1069e5fbf992ff8efccacb9db94e5959a5b3ba9bb903",
    "fonts/SourceHanSansCN-VF.otf.woff2": "7087698d52240614659957608d8c4ad446759aee3208409dc9f566412e7af8f4",
    "fonts/SourceHanSerifCN-VF.otf.woff2": "808cb3203bb9cdd6b166a8a656a0c7608a7dc2a31c41c2cd0374550cae445471",
}


def default_visual_plan() -> dict:
    return {
        "schemaVersion": 1,
        "mode": "article",
        "presetId": "current-editorial",
        "designLanguage": "bold-statement",
        "palette": {
            "paper": "oklch(0.985 0.004 80)",
            "paperAlt": "oklch(0.93 0.006 80)",
            "ink": "oklch(0.18 0.006 60)",
            "muted": "oklch(0.46 0.012 60)",
            "accent": "oklch(0.62 0.23 28)",
            "line": "oklch(0.30 0.01 60)",
        },
        "presentations": {
            "cover": "illustration-led",
            "heading": "editorial-print-led",
            "paragraph": "type-led",
            "quote": "editorial-print-led",
            "list": "type-led",
            "code": "panel-led",
            "table": "data-led",
            "diagram": "schematic-led",
            "media": "photo-led",
            "hr": "editorial-print-led",
        },
        "treatments": {"cover": "section-emphasis", "heading": "section-emphasis", "table": "dense"},
        "typography": {
            "fontFamily": "source-han-sans",
            "bodySize": 30,
            "lineHeight": 1.68,
            "characterWidth": 1.0,
            "pageMargin": 58,
        },
        "pageChrome": {
            "showPageNumber": True,
            "showDate": False,
            "date": "",
            "showAuthor": False,
            "author": "507",
        },
        "cover": {"title": "", "subtitle": "", "image": "", "author": "507"},
    }


def atomic_write(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        Path(temporary).unlink(missing_ok=True)
        raise


def atomic_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        Path(temporary).unlink(missing_ok=True)
        raise


def read_json(path: Path, fallback: dict | None = None) -> dict:
    if not path.is_file():
        return fallback or {}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} 必须是 JSON object")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def hash_json(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256_text(payload)


def runtime_sha256(runtime_dir: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in runtime_dir.rglob("*") if item.is_file() and "node_modules" not in item.parts):
        digest.update(str(path.relative_to(runtime_dir)).encode())
        digest.update(bytes.fromhex(sha256(path)))
    return digest.hexdigest()


def directory_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    if not root.is_dir():
        return digest.hexdigest()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(str(path.relative_to(root)).encode())
        digest.update(bytes.fromhex(sha256(path)))
    return digest.hexdigest()


def font_set_identity(runtime_dir: Path) -> str:
    digest = hashlib.sha256()
    for relative, expected in sorted(FONT_ASSETS.items()):
        path = runtime_dir / relative
        if not path.is_file():
            raise RuntimeError(f"缺少本地字体：{relative}")
        actual = sha256(path)
        if actual != expected:
            raise RuntimeError(f"本地字体哈希不一致：{relative}")
        digest.update(relative.encode("utf-8"))
        digest.update(bytes.fromhex(actual))
    return f"source-han-cn-ofl-v1:{digest.hexdigest()}"


class ProjectState:
    def __init__(self, project_dir: Path, runtime_dir: Path, source: Path | None, chrome: str | None):
        self.project_dir = project_dir.resolve()
        self.runtime_dir = runtime_dir.resolve()
        self.chrome = chrome
        self.token = secrets.token_urlsafe(24)
        self.base_url = ""
        self.lock = threading.RLock()
        self.project_dir.mkdir(parents=True, exist_ok=True)
        content_path = self.project_dir / "content.md"
        if not content_path.exists():
            initial = source.read_text(encoding="utf-8") if source else "# 未命名作品\n\n从这里开始编辑正文。\n"
            atomic_write(content_path, initial)
        plan_path = self.project_dir / "visual-plan.json"
        if not plan_path.exists():
            atomic_write(plan_path, json.dumps(default_visual_plan(), ensure_ascii=False, indent=2) + "\n")

    def safe_project_path(self, relative: str) -> Path:
        decoded = urllib.parse.unquote(relative).lstrip("/")
        candidate = (self.project_dir / decoded).resolve()
        try:
            candidate.relative_to(self.project_dir)
        except ValueError as exc:
            raise PermissionError("路径越出作品目录") from exc
        return candidate

    def project_payload(self) -> dict:
        with self.lock:
            return {
                "content": (self.project_dir / "content.md").read_text(encoding="utf-8"),
                "visualPlan": read_json(self.project_dir / "visual-plan.json", default_visual_plan()),
                "pagedContent": read_json(self.project_dir / "paged-content.json", {}),
                "runtimeVersion": RUNTIME_VERSION,
                "runtimeSha256": runtime_sha256(self.runtime_dir),
                "assetSetSha256": directory_sha256(self.project_dir / "assets"),
                "fontSet": font_set_identity(self.runtime_dir),
            }


def store_uploaded_image(state: ProjectState, payload: dict) -> dict:
    file_name = payload.get("fileName")
    data_url = payload.get("dataUrl")
    if not isinstance(file_name, str) or not file_name.strip():
        raise ValueError("上传图片缺少文件名")
    if not isinstance(data_url, str) or not data_url.startswith("data:image/") or ";base64," not in data_url:
        raise ValueError("上传内容必须是 base64 图片")
    header, encoded = data_url.split(",", 1)
    media_type = header.removeprefix("data:").split(";", 1)[0].lower()
    allowed_media = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp", "image/gif": ".gif"}
    if media_type not in allowed_media:
        raise ValueError("只支持 PNG、JPEG、WebP 和 GIF 图片")
    try:
        data = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("图片 base64 无效") from exc
    if not data or len(data) > MAX_IMAGE_BYTES:
        raise ValueError("图片为空或超过 10 MB")
    try:
        with Image.open(io.BytesIO(data)) as image:
            dimensions = image.size
            frame_count = getattr(image, "n_frames", 1)
            image.verify()
            detected = (image.format or "").upper()
    except Exception as exc:
        raise ValueError("上传内容不是有效图片") from exc
    if dimensions[0] <= 0 or dimensions[1] <= 0 or dimensions[0] * dimensions[1] > MAX_IMAGE_PIXELS:
        raise ValueError("图片像素尺寸无效或超过 6400 万像素")
    if frame_count > 1:
        raise ValueError("不支持动态图片，请上传静态 PNG、JPEG、WebP 或 GIF")
    formats = {"PNG": ".png", "JPEG": ".jpg", "WEBP": ".webp", "GIF": ".gif"}
    if detected not in formats:
        raise ValueError(f"不支持图片格式：{detected}")
    extension = formats[detected]
    stem = Path(file_name).stem.strip() or "image"
    safe_stem = "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in stem).strip("-")[:48] or "image"
    digest = hashlib.sha256(data).hexdigest()
    relative = Path("assets") / f"{safe_stem}-{digest[:12]}{extension}"
    with state.lock:
        target = state.safe_project_path(str(relative))
        if not target.exists():
            atomic_write_bytes(target, data)
    return {
        "path": str(relative),
        "alt": stem,
        "sha256": digest,
        "bytes": len(data),
        "width": dimensions[0],
        "height": dimensions[1],
        "assetSetSha256": directory_sha256(state.project_dir / "assets"),
    }


def json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("X-Content-Type-Options", "nosniff")
    handler.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
    handler.send_header("Referrer-Policy", "no-referrer")
    handler.end_headers()
    handler.wfile.write(body)


def serve_file(handler: BaseHTTPRequestHandler, path: Path, cache: bool = False) -> None:
    if not path.is_file():
        handler.send_error(HTTPStatus.NOT_FOUND)
        return
    body = path.read_bytes()
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    handler.send_response(HTTPStatus.OK)
    handler.send_header("Content-Type", mime)
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "public, max-age=31536000, immutable" if cache else "no-store")
    handler.send_header("X-Content-Type-Options", "nosniff")
    handler.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
    handler.send_header("Referrer-Policy", "no-referrer")
    handler.end_headers()
    handler.wfile.write(body)


def read_request_json(handler: BaseHTTPRequestHandler) -> dict:
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError as exc:
        raise ValueError("Content-Length 无效") from exc
    if length <= 0 or length > MAX_BODY_BYTES:
        raise ValueError("请求体为空或过大")
    value = json.loads(handler.rfile.read(length).decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError("请求体必须是 JSON object")
    return value


def chrome_command(chrome: str, profile: Path, output: Path, url: str) -> list[str]:
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
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=6000",
        "--force-device-scale-factor=2",
        "--window-size=750,1000",
        f"--user-data-dir={profile}",
        f"--screenshot={output}",
        url,
    ]


def stop_process_group(process: subprocess.Popen | None) -> None:
    if process is None or process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        process.wait()
        return
    try:
        process.wait(timeout=2)
        return
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def render_page_png(chrome: str, url: str, output: Path, timeout: float = 20) -> None:
    profile = Path(tempfile.mkdtemp(prefix="rednote-runtime-chrome-"))
    log = output.with_suffix(".chrome.log")
    process: subprocess.Popen | None = None
    try:
        with log.open("wb") as stream:
            process = subprocess.Popen(chrome_command(chrome, profile, output, url), stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
            deadline = time.time() + timeout
            last_size = -1
            stable = 0
            while time.time() < deadline:
                if output.exists() and output.stat().st_size:
                    size = output.stat().st_size
                    stable = stable + 1 if size == last_size else 0
                    last_size = size
                    if stable >= 3:
                        break
                if process.poll() is not None and not output.exists():
                    break
                time.sleep(0.2)
        if not output.is_file() or not output.stat().st_size:
            detail = log.read_text(encoding="utf-8", errors="ignore")[-1600:]
            raise RuntimeError(f"Chrome 页面导出失败：{detail}")
        with Image.open(output) as image:
            if image.size != (1500, 2000):
                raise RuntimeError(f"页面尺寸错误：{image.size}，应为 (1500, 2000)")
    finally:
        stop_process_group(process)
        log.unlink(missing_ok=True)
        shutil.rmtree(profile, ignore_errors=True)


def compile_project_headless(state: ProjectState, timeout: float = 25) -> dict:
    chrome = find_chrome(state.chrome)
    profile = Path(tempfile.mkdtemp(prefix="rednote-runtime-compile-"))
    dump = profile / "page.html"
    log = profile / "chrome.log"
    paged_path = state.project_dir / "paged-content.json"
    previous_mtime = paged_path.stat().st_mtime_ns if paged_path.exists() else -1
    url = f"{state.base_url}/?token={urllib.parse.quote(state.token)}"
    command = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--disable-background-networking",
        "--disable-component-update",
        "--disable-sync",
        "--no-first-run",
        "--no-default-browser-check",
        "--metrics-recording-only",
        "--virtual-time-budget=8000",
        "--window-size=1680,900",
        f"--user-data-dir={profile / 'profile'}",
        "--dump-dom",
        url,
    ]
    process: subprocess.Popen | None = None
    try:
        with dump.open("wb") as output, log.open("wb") as errors:
            process = subprocess.Popen(command, stdout=output, stderr=errors, start_new_session=True)
            deadline = time.time() + timeout
            while time.time() < deadline:
                if paged_path.exists() and paged_path.stat().st_mtime_ns != previous_mtime:
                    candidate = read_json(paged_path, {})
                    if candidate.get("status") in {"compiled", "invalid"}:
                        break
                if process.poll() is not None:
                    break
                time.sleep(0.2)
        paged = read_json(paged_path, {})
        if paged.get("status") != "compiled":
            detail = log.read_text(encoding="utf-8", errors="ignore")[-1600:]
            raise RuntimeError(f"无界面分页编译失败：{detail}")
        return paged
    finally:
        stop_process_group(process)
        shutil.rmtree(profile, ignore_errors=True)


def snapshot_html(page_count: int, extension: str) -> str:
    images = "\n".join(f'<figure><img src="pages/rednote_page_{index:02d}.{extension}" alt="第 {index} 页"></figure>' for index in range(1, page_count + 1))
    return f"""<!doctype html><html lang=\"zh-CN\"><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width\"><title>RedNote 预览</title><style>body{{margin:0;padding:24px;background:#d9d8d3;font-family:system-ui}}main{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:24px;max-width:1120px;margin:auto}}figure{{margin:0}}img{{display:block;width:100%;height:auto;box-shadow:0 12px 36px #2223}}</style><main>{images}</main></html>"""


def publish_candidate(candidate: Path, project_dir: Path) -> None:
    backup = Path(tempfile.mkdtemp(prefix="rednote-export-backup-", dir=project_dir.parent))
    moved: list[tuple[Path, Path]] = []
    try:
        for name in MANAGED_EXPORTS:
            target = project_dir / name
            if target.exists():
                destination = backup / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                os.replace(target, destination)
                moved.append((destination, target))
        for name in MANAGED_EXPORTS:
            source = candidate / name
            if source.exists():
                os.replace(source, project_dir / name)
    except Exception:
        for name in MANAGED_EXPORTS:
            target = project_dir / name
            if target.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
        for source, target in reversed(moved):
            target.parent.mkdir(parents=True, exist_ok=True)
            os.replace(source, target)
        raise
    finally:
        shutil.rmtree(backup, ignore_errors=True)
        shutil.rmtree(candidate, ignore_errors=True)


def export_project(state: ProjectState, fmt: str) -> dict:
    if fmt not in {"jpg", "png", "pdf"}:
        raise ValueError("导出格式只能是 jpg、png 或 pdf")
    with state.lock:
        paged = read_json(state.project_dir / "paged-content.json")
    if paged.get("status") != "compiled":
        raise ValueError("当前分页不是可导出的 compiled 状态")
    current_content = (state.project_dir / "content.md").read_text(encoding="utf-8")
    current_plan = read_json(state.project_dir / "visual-plan.json")
    expected_inputs = paged.get("inputs") or {}
    if expected_inputs.get("contentSha256") != sha256_text(current_content):
        raise ValueError("content.md 已变化，当前分页已过期")
    if expected_inputs.get("visualPlanSha256") != hash_json(current_plan):
        raise ValueError("visual-plan.json 已变化，当前分页已过期")
    if expected_inputs.get("runtimeSha256") != runtime_sha256(state.runtime_dir):
        raise ValueError("runtime bundle 已变化，当前分页已过期")
    if expected_inputs.get("assetSetSha256") != directory_sha256(state.project_dir / "assets"):
        raise ValueError("本地素材已变化，当前分页已过期")
    page_count = paged.get("pageCount")
    if not isinstance(page_count, int) or page_count < 1:
        raise ValueError("paged-content.json 缺少有效页数")
    chrome = find_chrome(state.chrome)
    candidate = Path(tempfile.mkdtemp(prefix=".rednote-export-", dir=state.project_dir))
    pages_dir = candidate / "pages"
    pages_dir.mkdir(parents=True)
    png_files: list[Path] = []
    try:
        for page in range(1, page_count + 1):
            png_path = pages_dir / f"rednote_page_{page:02d}.png"
            url = f"{state.base_url}/?token={urllib.parse.quote(state.token)}&export=1&page={page}"
            render_page_png(chrome, url, png_path)
            png_files.append(png_path)

        output_files: list[Path] = []
        if fmt == "png":
            output_files = png_files
        else:
            for png_path in png_files:
                jpg_path = png_path.with_suffix(".jpg")
                with Image.open(png_path).convert("RGB") as image:
                    image.save(jpg_path, "JPEG", quality=94, optimize=True, progressive=True)
                output_files.append(jpg_path)
                png_path.unlink()
        if fmt == "pdf":
            pdf_path = candidate / "rednote.pdf"
            opened = [Image.open(path).convert("RGB") for path in output_files]
            try:
                opened[0].save(pdf_path, "PDF", save_all=True, append_images=opened[1:], resolution=144)
            finally:
                for image in opened:
                    image.close()

        contact_files = output_files if output_files else png_files
        build_contact_sheet(contact_files, candidate / "contact-sheet.jpg")
        atomic_write(candidate / "rednote.html", snapshot_html(page_count, "png" if fmt == "png" else "jpg"))
        artifacts = []
        for path in sorted(item for item in candidate.rglob("*") if item.is_file()):
            artifacts.append({"path": str(path.relative_to(candidate)), "sha256": sha256(path), "bytes": path.stat().st_size})
        manifest = {
            "status": "rendered",
            "runtimeVersion": RUNTIME_VERSION,
            "runtimeSha256": runtime_sha256(state.runtime_dir),
            "mode": paged.get("mode"),
            "pageCount": page_count,
            "canvas": [1500, 2000],
            "inputs": paged.get("inputs", {}),
            "format": fmt,
            "tools": {"chrome": subprocess.check_output([chrome, "--version"], text=True).strip()},
            "artifacts": artifacts,
        }
        atomic_write(candidate / "render-manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
        with state.lock:
            publish_candidate(candidate, state.project_dir)
        return {"outputDir": str(state.project_dir), "pageCount": page_count, "format": fmt}
    except Exception:
        shutil.rmtree(candidate, ignore_errors=True)
        raise


def handler_factory(state: ProjectState):
    class Handler(BaseHTTPRequestHandler):
        server_version = "507RedNote/0.1"

        def log_message(self, format: str, *args) -> None:  # noqa: A003
            return

        def authorized(self) -> bool:
            return self.headers.get("X-Rednote-Token") == state.token or urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("token", [""])[0] == state.token

        def do_GET(self) -> None:  # noqa: N802
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path == "/":
                serve_file(self, state.runtime_dir / "index.html")
                return
            if parsed.path in {"/app.js", "/dist/app.js"}:
                serve_file(self, state.runtime_dir / "dist" / "app.js")
                return
            if parsed.path == "/styles.css":
                serve_file(self, state.runtime_dir / "styles.css")
                return
            if parsed.path.startswith("/fonts/"):
                font_root = (state.runtime_dir / "fonts").resolve()
                candidate = (state.runtime_dir / parsed.path.lstrip("/")).resolve()
                try:
                    candidate.relative_to(font_root)
                except ValueError:
                    self.send_error(HTTPStatus.FORBIDDEN)
                    return
                serve_file(self, candidate, cache=True)
                return
            if parsed.path == "/api/project":
                if not self.authorized():
                    json_response(self, HTTPStatus.FORBIDDEN, {"error": "访问令牌无效"})
                    return
                json_response(self, HTTPStatus.OK, state.project_payload())
                return
            if parsed.path.startswith("/project/"):
                if not self.authorized():
                    self.send_error(HTTPStatus.FORBIDDEN)
                    return
                try:
                    serve_file(self, state.safe_project_path(parsed.path.removeprefix("/project/")))
                except PermissionError:
                    self.send_error(HTTPStatus.FORBIDDEN)
                return
            self.send_error(HTTPStatus.NOT_FOUND)

        def do_POST(self) -> None:  # noqa: N802
            parsed = urllib.parse.urlparse(self.path)
            if not self.authorized():
                json_response(self, HTTPStatus.FORBIDDEN, {"error": "访问令牌无效"})
                return
            try:
                payload = read_request_json(self)
                if parsed.path == "/api/content":
                    value = payload.get("content")
                    if not isinstance(value, str):
                        raise ValueError("content 必须是字符串")
                    with state.lock:
                        atomic_write(state.project_dir / "content.md", value)
                    json_response(self, HTTPStatus.OK, {"saved": True})
                    return
                if parsed.path == "/api/visual-plan":
                    value = payload.get("visualPlan")
                    if not isinstance(value, dict):
                        raise ValueError("visualPlan 必须是 object")
                    with state.lock:
                        atomic_write(state.project_dir / "visual-plan.json", json.dumps(value, ensure_ascii=False, indent=2) + "\n")
                    json_response(self, HTTPStatus.OK, {"saved": True})
                    return
                if parsed.path == "/api/paged-content":
                    value = payload.get("pagedContent")
                    if not isinstance(value, dict) or value.get("schemaVersion") != 1:
                        raise ValueError("pagedContent schemaVersion 无效")
                    with state.lock:
                        atomic_write(state.project_dir / "paged-content.json", json.dumps(value, ensure_ascii=False, indent=2) + "\n")
                    json_response(self, HTTPStatus.OK, {"saved": True})
                    return
                if parsed.path == "/api/upload-image":
                    json_response(self, HTTPStatus.OK, store_uploaded_image(state, payload))
                    return
                if parsed.path == "/api/export":
                    result = export_project(state, str(payload.get("format", "jpg")).lower())
                    json_response(self, HTTPStatus.OK, result)
                    return
                json_response(self, HTTPStatus.NOT_FOUND, {"error": "接口不存在"})
            except (ValueError, PermissionError) as exc:
                json_response(self, HTTPStatus.BAD_REQUEST, {"error": str(exc)})
            except Exception as exc:  # pragma: no cover - surfaced to the UI
                json_response(self, HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(exc)})

    return Handler


def main() -> None:
    parser = argparse.ArgumentParser(description="启动 507-rednote 本地动态工作台")
    parser.add_argument("--project", required=True, help="作品的小红书输出目录")
    parser.add_argument("--source", help="首次创建 content.md 时使用的 Markdown 主稿")
    parser.add_argument("--chrome", help="Chrome / Chromium 可执行文件")
    parser.add_argument("--port", type=int, default=0, help="本地端口；默认自动选择")
    parser.add_argument("--no-open", action="store_true", help="不自动打开浏览器")
    parser.add_argument("--export", choices=("jpg", "png", "pdf"), help="跳过人工预览，使用同一 runtime 直接导出")
    args = parser.parse_args()

    project = Path(args.project).expanduser().resolve()
    source = Path(args.source).expanduser().resolve() if args.source else None
    if source and not source.is_file():
        raise SystemExit(f"主稿不存在：{source}")
    runtime_dir = Path(__file__).resolve().parent.parent / "runtime"
    if not (runtime_dir / "dist" / "app.js").is_file():
        raise SystemExit("runtime bundle 不存在；维护者需先在 runtime/ 运行 npm run build")
    font_set_identity(runtime_dir)
    state = ProjectState(project, runtime_dir, source, args.chrome)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler_factory(state))
    state.base_url = f"http://127.0.0.1:{server.server_address[1]}"
    url = f"{state.base_url}/?token={urllib.parse.quote(state.token)}"
    print(json.dumps({"status": "ready", "url": url, "project": str(project), "runtimeVersion": RUNTIME_VERSION}, ensure_ascii=False), flush=True)
    if args.export:
        thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.2}, daemon=True)
        thread.start()
        try:
            compile_project_headless(state)
            result = export_project(state, args.export)
            print(json.dumps({"status": "rendered", **result}, ensure_ascii=False), flush=True)
        finally:
            server.shutdown()
            thread.join(timeout=3)
            server.server_close()
        return
    if not args.no_open:
        webbrowser.open(url)
    try:
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
