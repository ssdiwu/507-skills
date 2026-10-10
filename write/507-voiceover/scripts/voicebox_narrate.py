#!/usr/bin/env python3
"""Generate verified narration audio through Voicebox's local REST API."""

from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import math
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import wave
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


DEFAULT_SERVER_URL = os.environ.get("VOICEBOX_URL", "http://127.0.0.1:17493")
CLIENT_ID = "507-narrate"
TERMINAL_STATUSES = {"completed", "failed", "cancelled", "canceled"}
SECTION_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")
DEFAULT_PRESET = "daily"
NARRATION_PRESETS: dict[str, dict[str, Any]] = {
    "daily": {"engine": "qwen", "model_size": "0.6B", "speed": 1.2},
    "precision": {"engine": "qwen", "model_size": "1.7B", "speed": 1.2},
}
MIN_TEMPO = 0.5
MAX_TEMPO = 2.0


class VoiceboxError(RuntimeError):
    """Raised when Voicebox cannot satisfy the narration contract."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _http_error_message(error: urllib.error.HTTPError) -> str:
    try:
        body = error.read().decode("utf-8", errors="replace").strip()
    except Exception:
        body = ""
    return f"HTTP {error.code}: {body or error.reason}"


def request_json(
    server_url: str,
    path: str,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    timeout: float = 30,
) -> Any:
    data = None
    headers = {"Accept": "application/json", "X-Voicebox-Client-Id": CLIENT_ID}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(
        f"{server_url.rstrip('/')}{path}",
        data=data,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except urllib.error.HTTPError as error:
        raise VoiceboxError(_http_error_message(error)) from error
    except urllib.error.URLError as error:
        raise VoiceboxError(f"Voicebox request failed: {error.reason}") from error
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise VoiceboxError(f"Voicebox returned invalid JSON for {path}") from error


def _is_loopback_host(hostname: str | None) -> bool:
    if not hostname:
        return False
    if hostname.casefold() == "localhost":
        return True
    try:
        return ipaddress.ip_address(hostname).is_loopback
    except ValueError:
        return False


def validate_server_url(server_url: str, allow_remote: bool) -> str:
    parsed = urllib.parse.urlparse(server_url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise VoiceboxError("Voicebox server URL must be an http(s) URL")
    if not allow_remote and not _is_loopback_host(parsed.hostname):
        raise VoiceboxError(
            "Refusing a non-loopback Voicebox server; pass --allow-remote only for an explicitly trusted server"
        )
    return server_url.rstrip("/")


def get_health(server_url: str, timeout: float = 5) -> dict[str, Any]:
    result = request_json(server_url, "/health", timeout=timeout)
    if not isinstance(result, dict):
        raise VoiceboxError("Voicebox health response is not an object")
    return result


def ensure_server(
    server_url: str,
    *,
    auto_start: bool,
    start_timeout: float,
) -> dict[str, Any]:
    try:
        health = get_health(server_url)
        if health.get("status") == "healthy":
            return health
    except VoiceboxError:
        pass

    if not auto_start:
        raise VoiceboxError("Voicebox is not healthy and automatic application start is disabled")
    if platform.system() != "Darwin":
        raise VoiceboxError("Start Voicebox manually on this platform, then run the command again")

    result = subprocess.run(
        ["open", "-a", "Voicebox"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        raise VoiceboxError(f"Could not start Voicebox: {result.stderr.strip()}")

    deadline = time.monotonic() + start_timeout
    last_error = "Voicebox did not become healthy"
    while time.monotonic() < deadline:
        try:
            health = get_health(server_url)
            if health.get("status") == "healthy":
                return health
            last_error = f"Voicebox status is {health.get('status')!r}"
        except VoiceboxError as error:
            last_error = str(error)
        time.sleep(0.5)
    raise VoiceboxError(f"{last_error} within {start_timeout:g} seconds")


def list_profiles(server_url: str) -> list[dict[str, Any]]:
    result = request_json(server_url, "/profiles")
    if not isinstance(result, list) or not all(isinstance(item, dict) for item in result):
        raise VoiceboxError("Voicebox profiles response is not a list")
    return result


def resolve_profile(
    profiles: list[dict[str, Any]], selector: str | None
) -> dict[str, Any]:
    if not profiles:
        raise VoiceboxError("Voicebox has no voice profile; create and approve one in the app first")
    if selector is None:
        if len(profiles) == 1:
            return profiles[0]
        raise VoiceboxError("Multiple voice profiles exist; choose one with --profile NAME_OR_ID")

    by_id = [profile for profile in profiles if profile.get("id") == selector]
    if len(by_id) == 1:
        return by_id[0]
    by_name = [profile for profile in profiles if profile.get("name") == selector]
    if len(by_name) == 1:
        return by_name[0]
    folded = [
        profile
        for profile in profiles
        if isinstance(profile.get("name"), str)
        and profile["name"].casefold() == selector.casefold()
    ]
    if len(folded) == 1:
        return folded[0]
    if len(folded) > 1:
        raise VoiceboxError(f"Voice profile name is ambiguous: {selector}")
    raise VoiceboxError(f"Voice profile was not found: {selector}")


def parse_sse_data(line: bytes | str) -> dict[str, Any] | None:
    text = line.decode("utf-8", errors="replace") if isinstance(line, bytes) else line
    text = text.strip()
    if not text.startswith("data:"):
        return None
    payload = text[5:].strip()
    if not payload:
        return None
    try:
        event = json.loads(payload)
    except json.JSONDecodeError as error:
        raise VoiceboxError("Voicebox status stream returned invalid JSON") from error
    if not isinstance(event, dict):
        raise VoiceboxError("Voicebox status event is not an object")
    return event


def wait_for_generation(
    server_url: str,
    generation_id: str,
    *,
    timeout: float,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    path = f"/generate/{urllib.parse.quote(generation_id, safe='')}/status"
    while time.monotonic() < deadline:
        remaining = max(1.0, deadline - time.monotonic())
        request = urllib.request.Request(
            f"{server_url}{path}",
            headers={
                "Accept": "text/event-stream, application/json",
                "Cache-Control": "no-cache",
                "X-Voicebox-Client-Id": CLIENT_ID,
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=min(60.0, remaining)) as response:
                content_type = response.headers.get_content_type()
                if content_type == "text/event-stream":
                    for line in response:
                        event = parse_sse_data(line)
                        if event is None:
                            continue
                        status = str(event.get("status", ""))
                        if status in TERMINAL_STATUSES:
                            if status != "completed":
                                raise VoiceboxError(
                                    f"Voicebox generation {status}: {event.get('error') or 'unknown error'}"
                                )
                            return event
                else:
                    raw = response.read()
                    try:
                        event = json.loads(raw.decode("utf-8"))
                    except (UnicodeDecodeError, json.JSONDecodeError) as error:
                        raise VoiceboxError("Voicebox status response is neither SSE nor JSON") from error
                    if isinstance(event, dict):
                        status = str(event.get("status", ""))
                        if status in TERMINAL_STATUSES:
                            if status != "completed":
                                raise VoiceboxError(
                                    f"Voicebox generation {status}: {event.get('error') or 'unknown error'}"
                                )
                            return event
        except urllib.error.HTTPError as error:
            raise VoiceboxError(_http_error_message(error)) from error
        except (urllib.error.URLError, TimeoutError):
            pass
        time.sleep(0.5)
    raise VoiceboxError(f"Voicebox generation timed out after {timeout:g} seconds")


def build_generation_payload(
    *,
    profile_id: str,
    text: str,
    language: str,
    engine: str | None,
    model_size: str | None,
    seed: int | None,
    instruct: str | None,
    normalize: bool,
    max_chunk_chars: int | None,
    crossfade_ms: int | None,
) -> dict[str, Any]:
    if not text.strip():
        raise VoiceboxError("Narration text cannot be empty")
    payload: dict[str, Any] = {
        "profile_id": profile_id,
        "text": text.strip(),
        "language": language,
        "normalize": normalize,
    }
    optional = {
        "engine": engine,
        "model_size": model_size,
        "seed": seed,
        "instruct": instruct,
        "max_chunk_chars": max_chunk_chars,
        "crossfade_ms": crossfade_ms,
    }
    payload.update({key: value for key, value in optional.items() if value is not None})
    return payload


def _prepare_output(path: Path, force: bool) -> Path:
    if path.suffix.casefold() != ".wav":
        raise VoiceboxError(f"Narration output must use the .wav extension: {path}")
    if path.exists() and not force:
        raise VoiceboxError(f"Output already exists; use --force to replace it: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def download_audio(
    server_url: str,
    generation_id: str,
    output: Path,
    *,
    force: bool,
) -> None:
    output = _prepare_output(output, force)
    request = urllib.request.Request(
        f"{server_url}/audio/{urllib.parse.quote(generation_id, safe='')}",
        headers={"Accept": "audio/wav", "X-Voicebox-Client-Id": CLIENT_ID},
    )
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output.name}.", suffix=".tmp", dir=output.parent
    )
    try:
        with os.fdopen(descriptor, "wb") as target:
            try:
                with urllib.request.urlopen(request, timeout=120) as response:
                    for chunk in iter(lambda: response.read(1024 * 1024), b""):
                        target.write(chunk)
            except urllib.error.HTTPError as error:
                raise VoiceboxError(_http_error_message(error)) from error
            except urllib.error.URLError as error:
                raise VoiceboxError(f"Could not download generated audio: {error.reason}") from error
        os.replace(temporary_name, output)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def inspect_wav(path: Path) -> dict[str, Any]:
    try:
        with wave.open(str(path), "rb") as audio:
            channels = audio.getnchannels()
            sample_rate = audio.getframerate()
            sample_width = audio.getsampwidth()
            frames = audio.getnframes()
    except (wave.Error, EOFError) as error:
        raise VoiceboxError(f"Generated file is not a readable PCM WAV: {path}") from error
    if channels < 1 or sample_rate < 1 or frames < 1:
        raise VoiceboxError(f"Generated WAV has no playable audio frames: {path}")
    duration = frames / sample_rate
    if duration <= 0:
        raise VoiceboxError(f"Generated WAV duration is zero: {path}")
    return {
        "format": "wav",
        "durationSeconds": round(duration, 6),
        "sampleRate": sample_rate,
        "channels": channels,
        "sampleWidthBytes": sample_width,
        "frames": frames,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def validate_speed(value: Any) -> float:
    try:
        speed = float(value)
    except (TypeError, ValueError) as error:
        raise VoiceboxError("Narration speed must be a number") from error
    if not math.isfinite(speed) or not MIN_TEMPO <= speed <= MAX_TEMPO:
        raise VoiceboxError(
            f"Narration speed must be between {MIN_TEMPO:g} and {MAX_TEMPO:g}"
        )
    return speed


def _temporary_wav_path(output: Path, label: str) -> Path:
    descriptor, name = tempfile.mkstemp(
        prefix=f".{output.stem}.{label}.", suffix=".wav", dir=output.parent
    )
    os.close(descriptor)
    os.unlink(name)
    return Path(name)


def apply_tempo(source: Path, output: Path, *, speed: float, force: bool) -> None:
    speed = validate_speed(speed)
    _prepare_output(output, force)
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise VoiceboxError(
            "FFmpeg is required for pitch-preserving narration speed adjustment"
        )
    temporary = _temporary_wav_path(output, "tempo")
    command = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(source),
        "-filter:a",
        f"atempo={speed:g}",
        "-c:a",
        "pcm_s16le",
        str(temporary),
    ]
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True)
        if result.returncode != 0:
            raise VoiceboxError(
                f"FFmpeg could not adjust narration speed: {result.stderr.strip()}"
            )
        inspect_wav(temporary)
        os.replace(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def get_server_version(server_url: str) -> str | None:
    try:
        spec = request_json(server_url, "/openapi.json")
    except VoiceboxError:
        return None
    if not isinstance(spec, dict):
        return None
    info = spec.get("info")
    return info.get("version") if isinstance(info, dict) else None


def _profile_receipt(profile: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": profile.get("id"),
        "name": profile.get("name"),
        "language": profile.get("language"),
        "voiceType": profile.get("voice_type"),
        "sampleCount": profile.get("sample_count"),
        "defaultEngine": profile.get("default_engine"),
    }


def generate_one(
    server_url: str,
    profile: dict[str, Any],
    text: str,
    output: Path,
    *,
    language: str,
    engine: str | None,
    model_size: str | None,
    seed: int | None,
    instruct: str | None,
    normalize: bool,
    max_chunk_chars: int | None,
    crossfade_ms: int | None,
    speed: float,
    timeout: float,
    force: bool,
) -> dict[str, Any]:
    _prepare_output(output, force)
    speed = validate_speed(speed)
    if speed != 1.0 and shutil.which("ffmpeg") is None:
        raise VoiceboxError(
            "FFmpeg is required for pitch-preserving narration speed adjustment"
        )
    payload = build_generation_payload(
        profile_id=str(profile["id"]),
        text=text,
        language=language,
        engine=engine,
        model_size=model_size,
        seed=seed,
        instruct=instruct,
        normalize=normalize,
        max_chunk_chars=max_chunk_chars,
        crossfade_ms=crossfade_ms,
    )
    initial = request_json(server_url, "/generate", method="POST", payload=payload, timeout=60)
    if not isinstance(initial, dict) or not initial.get("id"):
        raise VoiceboxError("Voicebox generation did not return an id")
    generation_id = str(initial["id"])
    if initial.get("status") == "completed":
        final = initial
    else:
        final = wait_for_generation(server_url, generation_id, timeout=timeout)
    source_output = output if speed == 1.0 else _temporary_wav_path(output, "source")
    try:
        download_audio(server_url, generation_id, source_output, force=True)
        source_audio = inspect_wav(source_output)
        if speed != 1.0:
            apply_tempo(source_output, output, speed=speed, force=force)
        audio = inspect_wav(output)
    finally:
        if source_output != output:
            source_output.unlink(missing_ok=True)
    return {
        "generationId": generation_id,
        "status": final.get("status", initial.get("status")),
        "serverDurationSeconds": final.get("duration", initial.get("duration")),
        "engine": initial.get("engine", payload.get("engine")),
        "modelSize": initial.get("model_size", payload.get("model_size")),
        "seed": initial.get("seed", payload.get("seed")),
        "instruct": initial.get("instruct", payload.get("instruct")),
        "language": initial.get("language", language),
        "text": payload["text"],
        "textSha256": sha256_bytes(payload["text"].encode("utf-8")),
        "speed": speed,
        "pitchPreserved": True,
        "sourceAudio": source_audio,
        "audio": {"path": str(output.resolve()), **audio},
    }


def safe_section_id(value: Any) -> str:
    if not isinstance(value, str) or not SECTION_ID_PATTERN.fullmatch(value):
        raise VoiceboxError(
            "Each section id must be 1-100 characters using letters, numbers, dot, underscore, or hyphen"
        )
    return value


def extract_capabilities(spec: dict[str, Any]) -> dict[str, Any]:
    schemas = spec.get("components", {}).get("schemas", {})
    request_schema = schemas.get("GenerationRequest", {})
    properties = request_schema.get("properties", {})

    def pattern_values(name: str) -> list[str]:
        field = properties.get(name, {})
        candidates = field.get("anyOf", [field])
        pattern = next(
            (candidate.get("pattern") for candidate in candidates if candidate.get("pattern")),
            None,
        )
        if not pattern:
            return []
        return pattern.removeprefix("^(").removesuffix(")$").split("|")

    return {
        "serverVersion": spec.get("info", {}).get("version"),
        "engines": pattern_values("engine"),
        "modelSizes": [value.replace("\\.", ".") for value in pattern_values("model_size")],
        "languages": pattern_values("language"),
        "defaults": {
            key: properties.get(key, {}).get("default")
            for key in ("language", "engine", "model_size", "max_chunk_chars", "crossfade_ms", "normalize")
        },
        "compatibilityNote": "Engine, profile type, language, and model-size compatibility is validated by the live Voicebox server.",
    }


def _require_authorized_voice(args: argparse.Namespace) -> None:
    if not args.authorized_voice:
        raise VoiceboxError(
            "Voice generation requires --authorized-voice to confirm ownership or explicit permission"
        )


def _read_text(args: argparse.Namespace) -> str:
    if args.text is not None:
        return args.text
    return args.text_file.read_text(encoding="utf-8")


def _effective_option(
    cli_value: Any,
    config: dict[str, Any],
    key: str,
    fallback: Any = None,
) -> Any:
    if cli_value is not None:
        return cli_value
    return config.get(key, fallback)


def resolve_generation_settings(
    args: argparse.Namespace,
    config: dict[str, Any],
    profile: dict[str, Any],
) -> dict[str, Any]:
    preset_name = _effective_option(args.preset, config, "preset", DEFAULT_PRESET)
    if preset_name not in NARRATION_PRESETS:
        choices = ", ".join(sorted(NARRATION_PRESETS))
        raise VoiceboxError(f"Unknown narration preset {preset_name!r}; choose {choices}")
    preset = NARRATION_PRESETS[preset_name]
    return {
        "preset": preset_name,
        "language": _effective_option(
            args.language, config, "language", profile.get("language") or "en"
        ),
        "engine": _effective_option(args.engine, config, "engine", preset["engine"]),
        "model_size": _effective_option(
            args.model_size, config, "model_size", preset["model_size"]
        ),
        "speed": validate_speed(
            _effective_option(args.speed, config, "speed", preset["speed"])
        ),
        "seed": _effective_option(args.seed, config, "seed"),
        "instruct": _effective_option(args.instruct, config, "instruct"),
        "normalize": _effective_option(args.normalize, config, "normalize", True),
        "max_chunk_chars": _effective_option(
            args.max_chunk_chars, config, "max_chunk_chars"
        ),
        "crossfade_ms": _effective_option(args.crossfade_ms, config, "crossfade_ms"),
    }


def command_health(args: argparse.Namespace, server_url: str) -> int:
    health = ensure_server(
        server_url, auto_start=not args.no_auto_start, start_timeout=args.start_timeout
    )
    print(json.dumps(health, ensure_ascii=False, indent=2))
    return 0


def command_profiles(args: argparse.Namespace, server_url: str) -> int:
    ensure_server(server_url, auto_start=not args.no_auto_start, start_timeout=args.start_timeout)
    profiles = [_profile_receipt(profile) for profile in list_profiles(server_url)]
    print(json.dumps(profiles, ensure_ascii=False, indent=2))
    return 0


def command_capabilities(args: argparse.Namespace, server_url: str) -> int:
    ensure_server(server_url, auto_start=not args.no_auto_start, start_timeout=args.start_timeout)
    spec = request_json(server_url, "/openapi.json")
    if not isinstance(spec, dict):
        raise VoiceboxError("Voicebox OpenAPI response is not an object")
    print(json.dumps(extract_capabilities(spec), ensure_ascii=False, indent=2))
    return 0


def command_generate(args: argparse.Namespace, server_url: str) -> int:
    _require_authorized_voice(args)
    manifest_path = args.output.with_suffix(".manifest.json")
    if manifest_path.exists() and not args.force:
        raise VoiceboxError(f"Manifest already exists; use --force to replace it: {manifest_path}")
    health = ensure_server(
        server_url, auto_start=not args.no_auto_start, start_timeout=args.start_timeout
    )
    profile = resolve_profile(list_profiles(server_url), args.profile)
    settings = resolve_generation_settings(args, {}, profile)
    result = generate_one(
        server_url,
        profile,
        _read_text(args),
        args.output,
        language=settings["language"],
        engine=settings["engine"],
        model_size=settings["model_size"],
        seed=settings["seed"],
        instruct=settings["instruct"],
        normalize=settings["normalize"],
        max_chunk_chars=settings["max_chunk_chars"],
        crossfade_ms=settings["crossfade_ms"],
        speed=settings["speed"],
        timeout=args.timeout,
        force=args.force,
    )
    manifest = {
        "schemaVersion": 2,
        "status": "completed",
        "createdAt": utc_now(),
        "generator": {"name": "voicebox-rest", "version": get_server_version(server_url)},
        "health": {
            key: health.get(key)
            for key in ("model_loaded", "model_downloaded", "model_size", "gpu_type", "backend_type", "backend_variant")
        },
        "profile": _profile_receipt(profile),
        "settings": {
            "preset": settings["preset"],
            "speed": settings["speed"],
            "pitchPreserved": True,
        },
        "result": result,
    }
    atomic_write_json(manifest_path, manifest)
    print(json.dumps({"audio": str(args.output.resolve()), "manifest": str(manifest_path.resolve()), "result": result}, ensure_ascii=False, indent=2))
    return 0


def load_batch_input(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        config: dict[str, Any] = {}
        sections = data
    elif isinstance(data, dict):
        config = data
        sections = data.get("sections")
    else:
        raise VoiceboxError("Batch input must be an object or a list of sections")
    if not isinstance(sections, list) or not sections:
        raise VoiceboxError("Batch input must contain at least one section")
    if not all(isinstance(section, dict) for section in sections):
        raise VoiceboxError("Every batch section must be an object")
    return config, sections


def resolve_batch_settings(
    args: argparse.Namespace,
    config: dict[str, Any],
    profile: dict[str, Any],
) -> dict[str, Any]:
    return resolve_generation_settings(args, config, profile)


def create_batch_manifest(
    args: argparse.Namespace,
    server_url: str,
    health: dict[str, Any],
    profile: dict[str, Any],
    settings: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schemaVersion": 2,
        "status": "partial",
        "createdAt": utc_now(),
        "source": str(args.input.resolve()),
        "sourceSha256": sha256_file(args.input),
        "generator": {"name": "voicebox-rest", "version": get_server_version(server_url)},
        "health": {
            key: health.get(key)
            for key in (
                "model_loaded",
                "model_downloaded",
                "model_size",
                "gpu_type",
                "backend_type",
                "backend_variant",
            )
        },
        "profile": _profile_receipt(profile),
        "settings": {
            "preset": settings["preset"],
            "language": settings["language"],
            "engine": settings["engine"],
            "modelSize": settings["model_size"],
            "seed": settings["seed"],
            "normalize": settings["normalize"],
            "maxChunkChars": settings["max_chunk_chars"],
            "crossfadeMs": settings["crossfade_ms"],
            "speed": settings["speed"],
            "pitchPreserved": True,
        },
        "sections": [],
        "totalDurationSeconds": 0.0,
    }


def preflight_batch_outputs(
    output_dir: Path,
    section_ids: list[str],
    *,
    force: bool,
) -> tuple[Path, list[Path]]:
    manifest_path = output_dir / "narration-manifest.json"
    audio_paths = [
        output_dir / f"{index:03d}-{section_id}.wav"
        for index, section_id in enumerate(section_ids, start=1)
    ]
    if not force:
        conflicts = [path for path in [manifest_path, *audio_paths] if path.exists()]
        if conflicts:
            formatted = ", ".join(str(path) for path in conflicts)
            raise VoiceboxError(
                f"Batch output already exists; use --force to replace it: {formatted}"
            )
    return manifest_path, audio_paths


def command_batch(args: argparse.Namespace, server_url: str) -> int:
    _require_authorized_voice(args)
    health = ensure_server(
        server_url, auto_start=not args.no_auto_start, start_timeout=args.start_timeout
    )
    config, sections = load_batch_input(args.input)
    profile = resolve_profile(list_profiles(server_url), args.profile or config.get("profile"))
    settings = resolve_batch_settings(args, config, profile)
    ids = [safe_section_id(section.get("id")) for section in sections]
    if len(set(ids)) != len(ids):
        raise VoiceboxError("Batch section ids must be unique")
    texts = [section.get("text") for section in sections]
    if not all(isinstance(text, str) and text.strip() for text in texts):
        raise VoiceboxError("Every batch section must contain non-empty text")
    manifest_path, audio_paths = preflight_batch_outputs(
        args.output_dir, ids, force=args.force
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)

    manifest = create_batch_manifest(args, server_url, health, profile, settings)
    atomic_write_json(manifest_path, manifest)

    cursor = 0.0
    for index, section in enumerate(sections, start=1):
        section_id = ids[index - 1]
        text = texts[index - 1]
        output = audio_paths[index - 1]
        result = generate_one(
            server_url,
            profile,
            text,
            output,
            language=settings["language"],
            engine=settings["engine"],
            model_size=settings["model_size"],
            seed=settings["seed"],
            instruct=section.get("instruct", config.get("instruct")),
            normalize=settings["normalize"],
            max_chunk_chars=settings["max_chunk_chars"],
            crossfade_ms=settings["crossfade_ms"],
            speed=settings["speed"],
            timeout=args.timeout,
            force=args.force,
        )
        duration = float(result["audio"]["durationSeconds"])
        end = cursor + duration
        manifest["sections"].append(
            {
                "id": section_id,
                "index": index,
                "text": result["text"],
                "textSha256": result["textSha256"],
                "audio": str(output.relative_to(args.output_dir)),
                "audioSha256": result["audio"]["sha256"],
                "startSeconds": round(cursor, 6),
                "endSeconds": round(end, 6),
                "durationSeconds": duration,
                "sourceDurationSeconds": result["sourceAudio"]["durationSeconds"],
                "speed": result["speed"],
                "pitchPreserved": result["pitchPreserved"],
                "generationId": result["generationId"],
                "engine": result["engine"],
                "modelSize": result["modelSize"],
                "instruct": result["instruct"],
            }
        )
        cursor = end
        manifest["totalDurationSeconds"] = round(cursor, 6)
        atomic_write_json(manifest_path, manifest)

    manifest["status"] = "completed"
    manifest["completedAt"] = utc_now()
    atomic_write_json(manifest_path, manifest)
    print(json.dumps({"manifest": str(manifest_path.resolve()), "sections": len(sections), "totalDurationSeconds": manifest["totalDurationSeconds"]}, ensure_ascii=False, indent=2))
    return 0


def add_common_generation_options(parser: argparse.ArgumentParser, *, defaults: bool) -> None:
    parser.add_argument("--profile", help="Exact Voicebox profile name or id")
    parser.add_argument(
        "--preset",
        choices=sorted(NARRATION_PRESETS),
        help="Narration preset; defaults to daily (Qwen 0.6B at 1.2x)",
    )
    parser.add_argument("--language", help="Narration language; defaults to the selected profile")
    parser.add_argument("--engine", help="Voicebox TTS engine; use the capabilities command to inspect current values")
    parser.add_argument("--model-size", help="Voicebox model size; compatibility depends on the selected engine")
    parser.add_argument(
        "--speed",
        type=float,
        help="Pitch-preserving final tempo; defaults to 1.2 for every preset",
    )
    parser.add_argument("--seed", type=int, help="Optional deterministic seed")
    parser.add_argument("--instruct", help="Optional delivery instruction supported by compatible engines")
    parser.add_argument(
        "--normalize",
        action=argparse.BooleanOptionalAction,
        default=True if defaults else None,
        help="Normalize output volume",
    )
    parser.add_argument("--max-chunk-chars", type=int, help="Maximum characters per long-text chunk")
    parser.add_argument("--crossfade-ms", type=int, help="Crossfade between long-text chunks")
    parser.add_argument("--timeout", type=float, default=900, help="Generation timeout per segment in seconds")
    parser.add_argument("--authorized-voice", action="store_true", help="Confirm ownership or explicit permission for the selected voice")
    parser.add_argument("--force", action="store_true", help="Replace existing output artifacts")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-url", default=DEFAULT_SERVER_URL, help="Voicebox REST server URL")
    parser.add_argument("--allow-remote", action="store_true", help="Allow an explicitly trusted non-loopback Voicebox server")
    parser.add_argument("--no-auto-start", action="store_true", help="Do not launch the Voicebox macOS app when the server is offline")
    parser.add_argument("--start-timeout", type=float, default=90, help="Seconds to wait for an automatically started server")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("health", help="Check or start Voicebox and print health")
    subparsers.add_parser("profiles", help="List available local voice profiles")
    subparsers.add_parser("capabilities", help="Read selectable engines, model sizes, and languages from the live API")

    generate = subparsers.add_parser("generate", help="Generate and verify one narration WAV")
    text_group = generate.add_mutually_exclusive_group(required=True)
    text_group.add_argument("--text", help="Narration text")
    text_group.add_argument("--text-file", type=Path, help="UTF-8 narration text file")
    generate.add_argument("--output", type=Path, required=True, help="Output .wav path")
    add_common_generation_options(generate, defaults=True)

    batch = subparsers.add_parser("batch", help="Generate section WAVs and a cumulative timing manifest")
    batch.add_argument("--input", type=Path, required=True, help="UTF-8 JSON section package")
    batch.add_argument("--output-dir", type=Path, required=True, help="Output directory")
    add_common_generation_options(batch, defaults=False)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        server_url = validate_server_url(args.server_url, args.allow_remote)
        commands = {
            "health": command_health,
            "profiles": command_profiles,
            "capabilities": command_capabilities,
            "generate": command_generate,
            "batch": command_batch,
        }
        return commands[args.command](args, server_url)
    except (VoiceboxError, OSError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
