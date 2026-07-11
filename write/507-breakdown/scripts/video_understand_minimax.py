#!/usr/bin/env python3
"""Mandatory MiniMax-M3 whole-video semantic understanding for breakdown."""
from __future__ import annotations

import argparse
import base64
import http.client
import json
import mimetypes
import os
import ssl
import sys
import uuid
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from video_contract import ANALYSIS_DIR, STATUS_SEMANTIC_FAILED, STATUS_UNDERSTOOD, VideoManifest, ensure_dir

MAX_VIDEO_BYTES = 512 * 1024 * 1024
DEFAULT_BASE_URL = "https://api.minimaxi.com"
DEFAULT_MODEL = "MiniMax-M3"
PROMPT_VERSION = "video_understanding_v1"

PROMPT = """Return JSON only. Understand this full video semantically, but do not claim verified timestamps, order, or direction. Return: {videoThesis, videoTypeHint, semanticUnits:[{id,meaning,spokenAnchors,visualAnchors,referencePosition,referenceTimeHint,status}]}. referencePosition/referenceTimeHint are incomplete references only; use status=unlocalized for every unit. Give searchable spoken and visual anchors for a separate local evidence locator."""


def mime_type(path: Path) -> str:
    return mimetypes.guess_type(path.name)[0] or "video/mp4"


def streamed_upload(base_url: str, api_key: str, video: Path) -> str:
    size = video.stat().st_size
    if size > MAX_VIDEO_BYTES:
        raise RuntimeError(f"视频超过 MiniMax 512MB 上限：{size} bytes")
    parsed = urlparse(base_url)
    if parsed.scheme != "https":
        raise RuntimeError("MiniMax API base URL 必须为 https")
    boundary = f"----507breakdown{uuid.uuid4().hex}"
    prefix = (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"purpose\"\r\n\r\nvideo_understanding\r\n"
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{video.name}\"\r\n"
        f"Content-Type: {mime_type(video)}\r\n\r\n"
    ).encode()
    suffix = f"\r\n--{boundary}--\r\n".encode()
    connection = http.client.HTTPSConnection(parsed.netloc, context=ssl.create_default_context(), timeout=180)
    path = (parsed.path.rstrip("/") + "/v1/files/upload") if parsed.path else "/v1/files/upload"
    connection.putrequest("POST", path)
    connection.putheader("Authorization", f"Bearer {api_key}")
    connection.putheader("Content-Type", f"multipart/form-data; boundary={boundary}")
    connection.putheader("Content-Length", str(len(prefix) + size + len(suffix)))
    connection.endheaders()
    connection.send(prefix)
    with video.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            connection.send(chunk)
    connection.send(suffix)
    response = connection.getresponse()
    payload = response.read().decode("utf-8", errors="replace")
    if response.status >= 300:
        raise RuntimeError(f"MiniMax Files API 失败 ({response.status}): {payload[:300]}")
    file_id = json.loads(payload).get("file", {}).get("file_id")
    if not file_id:
        raise RuntimeError("MiniMax Files API 未返回 file_id")
    return f"mm_file://{file_id}"


def parse_json_lenient(text: str) -> dict:
    """Parse one JSON object, allowing prose/fences around (not inside) it."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    try:
        return json.loads(text, strict=False)
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    if start == -1:
        raise RuntimeError("MiniMax 返回不含 JSON 对象")
    depth = 0
    in_string = False
    escaped = False
    end = None
    for i, char in enumerate(text[start:], start):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end is None:
        raise RuntimeError("MiniMax 返回的 JSON 对象未闭合")
    try:
        return json.loads(text[start:end], strict=False)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"MiniMax 返回的 JSON 无法解析（位置 {exc.pos}）: {text[:200]}...") from exc


def analyze(base_url: str, api_key: str, model: str, ref: str, fps: float, thinking: bool) -> dict:
    body = {
        "model": model,
        "max_tokens": 8000,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": PROMPT},
            {"type": "video", "source": {"type": "url", "url": ref, "fps": fps}},
        ]}],
    }
    if thinking:
        body["thinking"] = {"type": "adaptive"}
    import time as _time
    last_exc = None
    for attempt in range(3):
        request = Request(
            base_url.rstrip("/") + "/anthropic/v1/messages",
            data=json.dumps(body).encode(),
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json", "anthropic-version": "2023-06-01"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=300) as response:
                payload = json.loads(response.read().decode())
            break
        except Exception as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500] if hasattr(exc, "read") else ""
            last_exc = exc
            if attempt < 2 and "500" in str(exc):
                _time.sleep(5)
                continue
            raise RuntimeError(f"MiniMax /anthropic 请求失败：{exc} {detail}") from exc
    else:
        raise RuntimeError(f"MiniMax /anthropic 请求失败（重试 3 次）：{last_exc}") from last_exc
    text = "".join(item.get("text", "") for item in payload.get("content", []) if item.get("type") == "text").strip()
    result = parse_json_lenient(text)
    if not isinstance(result.get("semanticUnits"), list) or not result["semanticUnits"]:
        raise RuntimeError("MiniMax 语义结果缺少非空 semanticUnits")
    if not isinstance(result.get("videoThesis"), str) or not result["videoThesis"].strip():
        raise RuntimeError("MiniMax 语义结果缺少非空 videoThesis")
    if not isinstance(result.get("videoTypeHint"), str) or not result["videoTypeHint"].strip():
        raise RuntimeError("MiniMax 语义结果缺少非空 videoTypeHint")
    required_fields = {"id", "meaning", "spokenAnchors", "visualAnchors", "referencePosition", "referenceTimeHint"}
    for i, unit in enumerate(result["semanticUnits"]):
        missing = required_fields - set(unit)
        if missing:
            raise RuntimeError(f"semanticUnits[{i}] 缺少字段：{missing}")
        if not isinstance(unit.get("id"), str) or not unit["id"].strip():
            raise RuntimeError(f"semanticUnits[{i}].id 必须为非空字符串")
        if not isinstance(unit.get("meaning"), str) or not unit["meaning"].strip():
            raise RuntimeError(f"semanticUnits[{i}].meaning 必须为非空字符串")
        if not isinstance(unit.get("spokenAnchors"), list) or not isinstance(unit.get("visualAnchors"), list):
            raise RuntimeError(f"semanticUnits[{i}] 的 spokenAnchors/visualAnchors 必须为数组")
        if not all(isinstance(x, str) for x in unit["spokenAnchors"]):
            raise RuntimeError(f"semanticUnits[{i}].spokenAnchors 元素必须为字符串")
        if not all(isinstance(x, str) for x in unit["visualAnchors"]):
            raise RuntimeError(f"semanticUnits[{i}].visualAnchors 元素必须为字符串")
        if not isinstance(unit.get("referencePosition"), str):
            raise RuntimeError(f"semanticUnits[{i}].referencePosition 必须为字符串")
        if not isinstance(unit.get("referenceTimeHint"), str):
            raise RuntimeError(f"semanticUnits[{i}].referenceTimeHint 必须为字符串")
        unit["status"] = "unlocalized"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="MiniMax-M3 整段视频理解")
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--model", default=os.getenv("MINIMAX_VIDEO_MODEL", DEFAULT_MODEL))
    parser.add_argument("--fps", type=float, default=1)
    parser.add_argument("--thinking", action="store_true")
    parser.add_argument("--base-url", default=os.getenv("MINIMAX_API_BASE_URL", DEFAULT_BASE_URL))
    args = parser.parse_args()
    workspace = Path(args.workspace).expanduser().resolve()
    manifest = VideoManifest.load(workspace)
    api_key = os.getenv("MiniMax_API_KEY")
    if not api_key:
        manifest.set_status(STATUS_SEMANTIC_FAILED)
        manifest.step("video_understanding_minimax", "failed", "未设置 MiniMax_API_KEY")
        raise SystemExit("MiniMax_API_KEY 未导出；脚本不会读取 ~/.zshrc")
    video_path = Path(manifest.data.get("videoPath") or "")
    try:
        ref = streamed_upload(args.base_url, api_key, video_path)
        result = analyze(args.base_url, api_key, args.model, ref, args.fps, args.thinking)
        result["provenance"] = {"model": args.model, "fps": args.fps, "thinking": args.thinking, "promptVersion": PROMPT_VERSION, "videoHash": manifest.data.get("videoHash")}
        analysis_dir = workspace / ANALYSIS_DIR
        ensure_dir(analysis_dir)
        out = analysis_dir / "video_understanding_minimax.json"
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        (analysis_dir / "video_understanding_minimax.md").write_text("# MiniMax 视频理解\n\n> 未验证的语义参考，不是时间事实。\n\n```json\n" + json.dumps(result, ensure_ascii=False, indent=2) + "\n```\n", encoding="utf-8")
        manifest.step("video_understanding_minimax", "success", "MiniMax-M3 整段理解完成", str(out), model=args.model, fps=args.fps, promptVersion=PROMPT_VERSION)
        manifest.set_status(STATUS_UNDERSTOOD)
        print(out)
    except Exception as exc:
        manifest.set_status(STATUS_SEMANTIC_FAILED)
        manifest.step("video_understanding_minimax", "failed", str(exc)[:500])
        raise
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
