#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, Optional

from PIL import Image, ImageDraw, ImageFont


SUBTITLE_EXTENSIONS = {".srt", ".vtt", ".ass", ".lrc"}
MEDIA_EXCLUDED_EXTENSIONS = SUBTITLE_EXTENSIONS | {".json"}


def run_cmd(command, *, check=True, capture_output=False, text=True):
    return subprocess.run(command, check=check, capture_output=capture_output, text=text)


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "video"


def check_binary(name: str) -> bool:
    return shutil.which(name) is not None


def format_seconds(seconds: int) -> str:
    minutes, secs = divmod(max(0, int(seconds)), 60)
    return f"{minutes:02d}:{secs:02d}"


def timestamp_to_seconds(value: str) -> int:
    value = value.strip().replace(",", ".")
    if value.count(":") == 2:
        hours, minutes, seconds = value.split(":")
        return int(hours) * 3600 + int(minutes) * 60 + int(float(seconds))
    minutes, seconds = value.split(":")
    return int(minutes) * 60 + int(float(seconds))


@dataclass
class StepResult:
    status: str
    detail: str
    output: Optional[str] = None


@dataclass
class Segment:
    start: int
    end: int
    text: str

    def to_line(self) -> str:
        return f"[{format_seconds(self.start)}-{format_seconds(self.end)}] {self.text.strip()}"

    def to_window(self, source: str) -> dict:
        return {
            "start": format_seconds(self.start),
            "end": format_seconds(self.end),
            "source": source,
            "text": self.text.strip(),
        }


class Manifest:
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.raw_dir = workspace / "raw"
        self.path = self.raw_dir / "manifest.json"
        self.data = {
            "status": "running",
            "videoInput": None,
            "videoPath": None,
            "videoId": None,
            "titleHint": None,
            "lang": None,
            "steps": {},
            "textEvidenceSource": None,
            "notes": [],
        }

    def update(self, key, value):
        self.data[key] = value
        self.flush()

    def step(self, name: str, result: StepResult):
        self.data["steps"][name] = asdict(result)
        self.flush()

    def note(self, message: str):
        self.data["notes"].append(message)
        self.flush()

    def flush(self):
        ensure_dir(self.raw_dir)
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")


def detect_video_id(video: str) -> Optional[str]:
    if "bilibili.com/video/" in video:
        match = re.search(r"/video/([^/?]+)", video)
        return match.group(1) if match else None
    if "youtube.com/watch" in video or "youtu.be/" in video:
        match = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]+)", video)
        return match.group(1) if match else None
    return None


def build_workspace(base_dir: Path, video: str, title_hint: Optional[str], force: bool) -> Path:
    video_id = detect_video_id(video)
    if video_id:
        name = video_id
    elif title_hint:
        name = slugify(title_hint)
    else:
        candidate = Path(video)
        name = slugify(candidate.stem if candidate.exists() else "video")

    workspace = base_dir / name
    if workspace.exists() and not force:
        raise SystemExit(f"工作区已存在：{workspace}\n如需覆盖，请显式传 --force")
    if workspace.exists() and force:
        shutil.rmtree(workspace)
    ensure_dir(workspace / "raw")
    return workspace


def check_env() -> int:
    checks = {
        "ffmpeg": check_binary("ffmpeg"),
        "yt-dlp": check_binary("yt-dlp"),
        "tesseract": check_binary("tesseract"),
        "video_asr_venv": (Path.home() / ".venvs" / "video-asr" / "bin" / "python").exists(),
    }
    print(json.dumps(checks, ensure_ascii=False, indent=2))
    return 0 if checks["ffmpeg"] and checks["yt-dlp"] else 1


def download_or_copy_video(video: str, manifest: Manifest) -> Path:
    video_dir = manifest.raw_dir / "video"
    ensure_dir(video_dir)

    if video.startswith("http://") or video.startswith("https://"):
        out_template = str(video_dir / "video.%(ext)s")
        cmd = [
            "yt-dlp",
            "-o", out_template,
            "--write-info-json",
            "--write-subs",
            "--write-auto-subs",
            "--sub-langs", "all",
            video,
        ]
        try:
            run_cmd(cmd)
        except subprocess.CalledProcessError as exc:
            manifest.step("download_video", StepResult("failed", f"yt-dlp 下载失败：{exc.stderr or exc}"))
            raise
        candidates = sorted(video_dir.glob("video.*"))
        media = [p for p in candidates if p.suffix.lower() not in MEDIA_EXCLUDED_EXTENSIONS]
        if not media:
            manifest.step("download_video", StepResult("failed", "yt-dlp 执行后未找到视频文件"))
            raise SystemExit("yt-dlp 执行后没有找到下载下来的视频文件")
        video_path = media[0]
        manifest.step("download_video", StepResult("success", "已通过 yt-dlp 下载视频及平台字幕", str(video_path)))
        info_json = next(video_dir.glob("video.info.json"), None)
        if info_json and info_json.exists():
            info = json.loads(info_json.read_text(encoding="utf-8"))
            manifest.update("titleHint", info.get("title"))
            manifest.update("videoId", info.get("id"))
        return video_path

    source = Path(video).expanduser().resolve()
    if not source.exists():
        raise SystemExit(f"本地视频不存在：{source}")
    dest = video_dir / source.name
    shutil.copy2(source, dest)
    manifest.step("download_video", StepResult("success", "已复制本地视频", str(dest)))
    return dest


def parse_srt_or_vtt(lines: Iterable[str]) -> list[Segment]:
    content = [line.rstrip("\n") for line in lines]
    segments = []
    index = 0
    while index < len(content):
        line = content[index].strip()
        if not line or line.isdigit() or line == "WEBVTT":
            index += 1
            continue
        if "-->" not in line:
            index += 1
            continue
        start_raw, end_raw = [part.strip().split(" ")[0] for part in line.split("-->")[:2]]
        start = timestamp_to_seconds(start_raw)
        end = timestamp_to_seconds(end_raw)
        index += 1
        text_lines = []
        while index < len(content) and content[index].strip():
            candidate = content[index].strip()
            if not candidate.startswith("NOTE"):
                text_lines.append(re.sub(r"<[^>]+>", "", candidate))
            index += 1
        text = " ".join(part for part in text_lines if part).strip()
        if text:
            segments.append(Segment(start=start, end=end, text=text))
        index += 1
    return segments


def parse_ass(lines: Iterable[str]) -> list[Segment]:
    segments: list[Segment] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line.startswith('Dialogue:'):
            continue
        parts = line.split(',', 9)
        if len(parts) < 10:
            continue
        start_raw = parts[1].strip()
        end_raw = parts[2].strip()
        text = parts[9].strip()
        text = re.sub(r"\{[^}]+\}", "", text).replace('\\N', ' ').replace('\\n', ' ')
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            continue
        segments.append(
            Segment(
                start=timestamp_to_seconds(start_raw),
                end=timestamp_to_seconds(end_raw),
                text=text,
            )
        )
    return segments


def parse_lrc(lines: Iterable[str]) -> list[Segment]:
    raw = [line.strip() for line in lines if line.strip()]
    segments: list[Segment] = []
    for line in raw:
        matches = re.findall(r"\[(\d{2}:\d{2}(?:\.\d+)?)\]", line)
        if not matches:
            continue
        text = re.sub(r"\[[^\]]+\]", "", line).strip()
        if not text:
            continue
        for i, stamp in enumerate(matches):
            start = timestamp_to_seconds(stamp)
            end = start + 2
            segments.append(Segment(start=start, end=end, text=text))
    return segments


def normalize_segments(segments: list[Segment]) -> list[Segment]:
    normalized: list[Segment] = []
    for segment in segments:
        text = re.sub(r"\s+", " ", segment.text).strip()
        if not text:
            continue
        if normalized and normalized[-1].text == text and abs(normalized[-1].start - segment.start) <= 1:
            normalized[-1].end = max(normalized[-1].end, segment.end)
            continue
        normalized.append(Segment(start=segment.start, end=max(segment.end, segment.start + 1), text=text))
    return normalized


def load_segments_from_file(path: Path) -> list[Segment]:
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    if path.suffix.lower() in {".srt", ".vtt"}:
        segments = parse_srt_or_vtt(lines)
    elif path.suffix.lower() == ".ass":
        segments = parse_ass(lines)
    elif path.suffix.lower() == ".lrc":
        segments = parse_lrc(lines)
    else:
        segments = []
    return normalize_segments(segments)


def write_transcript_segments(segments: list[Segment], output_path: Path):
    output_path.write_text("\n".join(segment.to_line() for segment in segments), encoding="utf-8")


def choose_preferred_subtitle(subtitle_files: list[Path], lang: Optional[str]) -> Path:
    lang = (lang or "").lower()
    if lang:
        for file in subtitle_files:
            if f".{lang}" in file.name.lower() or f"-{lang}" in file.name.lower():
                return file
    for file in subtitle_files:
        name = file.name.lower()
        if ".zh" in name or ".en" in name:
            return file
    return subtitle_files[0]


def gather_platform_subtitles(manifest: Manifest, lang: Optional[str]) -> Optional[Path]:
    video_dir = manifest.raw_dir / "video"
    subs_dir = manifest.raw_dir / "subtitles"
    ensure_dir(subs_dir)

    subtitle_files = []
    for pattern in ("*.srt", "*.vtt", "*.ass", "*.lrc"):
        subtitle_files.extend(video_dir.glob(pattern))
    subtitle_files = sorted(subtitle_files)

    if not subtitle_files:
        manifest.step("platform_subtitles", StepResult("failed", "未找到平台原生字幕或自动字幕"))
        return None

    for file in subtitle_files:
        shutil.copy2(file, subs_dir / file.name)

    preferred = choose_preferred_subtitle(subtitle_files, lang)
    segments = load_segments_from_file(preferred)
    if not segments:
        manifest.step("platform_subtitles", StepResult("failed", f"字幕文件存在但未解析出有效内容：{preferred.name}"))
        return None

    transcript_path = subs_dir / "transcript.txt"
    write_transcript_segments(segments, transcript_path)
    manifest.update("textEvidenceSource", "platform-subtitles")
    manifest.step("platform_subtitles", StepResult("success", f"已收集并标准化平台字幕：{preferred.name}", str(transcript_path)))
    return transcript_path


def extract_audio_asr(video_path: Path, manifest: Manifest, lang: Optional[str]) -> Optional[Path]:
    asr_dir = manifest.raw_dir / "asr"
    ensure_dir(asr_dir)
    audio_path = asr_dir / "audio.wav"
    transcript_path = asr_dir / "transcript.txt"

    ffmpeg_cmd = [
        "ffmpeg", "-y", "-i", str(video_path), "-vn",
        "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", str(audio_path),
    ]
    try:
        run_cmd(ffmpeg_cmd)
    except subprocess.CalledProcessError as exc:
        manifest.step("local_asr", StepResult("failed", f"抽音频失败：{exc}"))
        return None

    python_bin = Path.home() / ".venvs" / "video-asr" / "bin" / "python"
    if not python_bin.exists():
        manifest.step("local_asr", StepResult("failed", "未找到 ~/.venvs/video-asr/bin/python"))
        return None

    helper_script = Path(__file__).with_name("asr_faster_whisper.py")
    try:
        run_cmd([
            str(python_bin),
            str(helper_script),
            str(audio_path),
            str(transcript_path),
            "--language",
            lang or "auto",
        ], capture_output=True)
    except subprocess.CalledProcessError as exc:
        manifest.step("local_asr", StepResult("failed", f"faster-whisper 执行失败：{exc.stderr or exc}"))
        return None

    transcript_text = transcript_path.read_text(encoding="utf-8", errors="ignore").strip()
    if not transcript_text:
        manifest.step("local_asr", StepResult("failed", "ASR 已执行，但未产出有效文字"))
        return None

    manifest.update("textEvidenceSource", "local-asr")
    manifest.step("local_asr", StepResult("success", "已完成本地 ASR", str(transcript_path)))
    return transcript_path


def extract_frames(video_path: Path, out_dir: Path, mode: str) -> int:
    ensure_dir(out_dir)
    pattern = out_dir / "frame_%05d.jpg"
    if mode == "uniform":
        vf = "fps=1"
        result = run_cmd(["ffmpeg", "-y", "-i", str(video_path), "-vf", vf, "-fps_mode", "vfr", "-q:v", "2", str(pattern)])
    else:
        vf = "select='gt(scene,0.25)'"
        result = run_cmd(["ffmpeg", "-y", "-i", str(video_path), "-vf", vf, "-fps_mode", "vfr", "-q:v", "2", str(pattern)], check=False)
        generated = list(out_dir.glob("frame_*.jpg"))
        if result.returncode != 0 and not generated:
            return 0
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, result.args)
    return len(list(out_dir.glob("frame_*.jpg")))


def make_contact_sheets(frames_dir: Path, contact_dir: Path) -> list[Path]:
    ensure_dir(contact_dir)
    frames = sorted(frames_dir.glob("frame_*.jpg"))
    if not frames:
        return []

    thumb_w, thumb_h = 640, 360
    cols, rows = 4, 2
    font = ImageFont.load_default()
    output: list[Path] = []

    for index in range(0, len(frames), cols * rows):
        chunk = frames[index:index + cols * rows]
        sheet = Image.new("RGB", (cols * thumb_w, rows * thumb_h), color=(0, 0, 0))
        draw = ImageDraw.Draw(sheet)
        for item_index, frame_path in enumerate(chunk):
            col = item_index % cols
            row = item_index // cols
            x = col * thumb_w
            y = row * thumb_h
            with Image.open(frame_path) as image:
                resized = image.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
                sheet.paste(resized, (x, y))
            label = frame_path.stem.replace("frame_", "")
            draw.rectangle([x + 8, y + 8, x + 128, y + 34], fill=(0, 0, 0))
            draw.text((x + 12, y + 12), label, fill=(255, 255, 255), font=font)

        out_path = contact_dir / f"sheet_{index // (cols * rows) + 1:03d}.jpg"
        sheet.save(out_path)
        output.append(out_path)
    return output


def run_ocr_on_frames(frames_dir: Path, ocr_dir: Path) -> list[Segment]:
    ensure_dir(ocr_dir)
    temp_dir = ocr_dir / "temp"
    ensure_dir(temp_dir)
    helper_script = Path(__file__).with_name("ocr_tesseract.py")
    frames = sorted(frames_dir.glob("frame_*.jpg"))
    sampled = frames[::2] or frames
    segments: list[Segment] = []
    last_text = None
    for frame in sampled:
        match = re.search(r"frame_(\d+)", frame.stem)
        frame_index = int(match.group(1)) - 1 if match else 0
        start = frame_index
        output_path = temp_dir / f"{frame.stem}.txt"
        run_cmd([sys.executable, str(helper_script), str(frame), str(output_path)], capture_output=True)
        text = output_path.read_text(encoding="utf-8", errors="ignore").strip()
        text = re.sub(r"\s+", " ", text)
        if len(text) < 2 or text == last_text:
            continue
        last_text = text
        segments.append(Segment(start=start, end=start + 2, text=text))
    return normalize_segments(segments)


def maybe_ocr(manifest: Manifest) -> Optional[Path]:
    if not check_binary("tesseract"):
        manifest.step("ocr", StepResult("failed", "本机未安装 tesseract，跳过 OCR"))
        return None
    frames_dir = manifest.raw_dir / "frames_uniform"
    if not frames_dir.exists() or not list(frames_dir.glob("frame_*.jpg")):
        manifest.step("ocr", StepResult("failed", "未找到可供 OCR 的原始帧"))
        return None
    ocr_dir = manifest.raw_dir / "ocr"
    try:
        segments = run_ocr_on_frames(frames_dir, ocr_dir)
    except subprocess.CalledProcessError as exc:
        manifest.step("ocr", StepResult("failed", f"OCR 执行失败：{exc.stderr or exc}"))
        return None
    if not segments:
        manifest.step("ocr", StepResult("failed", "OCR 已运行，但未识别出有效文字"))
        return None
    transcript_path = ocr_dir / "transcript.txt"
    write_transcript_segments(segments, transcript_path)
    manifest.update("textEvidenceSource", "ocr")
    manifest.step("ocr", StepResult("success", "已完成 OCR 兜底", str(transcript_path)))
    return transcript_path


def load_timestamped_segments(transcript_path: Path, source: str) -> list[Segment]:
    segments: list[Segment] = []
    for line in transcript_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        match = re.match(r"\[(\d{2}:\d{2})-(\d{2}:\d{2})\]\s*(.+)", line)
        if match:
            start, end, text = match.groups()
            segments.append(Segment(start=timestamp_to_seconds(start), end=timestamp_to_seconds(end), text=text))
        else:
            segments.append(Segment(start=0, end=0, text=line))
    return normalize_segments(segments)


def create_windows_jsonl(manifest: Manifest, transcript_path: Optional[Path]) -> Path:
    windows_path = manifest.raw_dir / "windows.jsonl"
    entries = []
    if transcript_path and transcript_path.exists():
        for segment in load_timestamped_segments(transcript_path, manifest.data.get("textEvidenceSource") or "unknown"):
            entries.append(segment.to_window(manifest.data.get("textEvidenceSource") or "unknown"))
    windows_path.write_text("\n".join(json.dumps(item, ensure_ascii=False) for item in entries), encoding="utf-8")
    return windows_path


def write_analysis_templates(workspace: Path, transcript_path: Optional[Path], manifest: Manifest):
    transcript_out = workspace / "transcript.md"
    meta_out = workspace / "meta.md"
    breakdown_md = workspace / "breakdown.md"
    breakdown_json = workspace / "breakdown.json"

    transcript_lines = []
    if transcript_path and transcript_path.exists():
        transcript_lines = transcript_path.read_text(encoding="utf-8").splitlines()

    transcript_content = "# Transcript\n\n"
    transcript_content += f"- 文字来源：`{manifest.data.get('textEvidenceSource') or 'unknown'}`\n\n"
    transcript_content += "## 原始文字\n\n"
    transcript_content += "\n".join(transcript_lines) if transcript_lines else "（暂无可用文字）"

    meta_content = "# Meta\n\n"
    meta_content += "- `video_type`：待 agent 基于 `transcript.md`、`raw/contact_sheets/` 与关键原始帧判定\n"
    meta_content += "- `status`：evidence-ready\n"
    meta_content += f"- `text_evidence_source`：`{manifest.data.get('textEvidenceSource') or 'unknown'}`\n"
    meta_content += f"- `workspace`：`{workspace}`\n"
    meta_content += f"- `manifest`：`{manifest.path}`\n"

    breakdown_md_content = "# Breakdown\n\n"
    breakdown_md_content += "> 这是证据包模板，不是最终拉片结论。Agent 必须先读 `transcript.md`，再看 `raw/contact_sheets/`，必要时回看 `raw/frames_uniform/` 与 `raw/frames_scenecut/` 后填写。\n\n"
    breakdown_md_content += "## 一句话主旨\n\n（待 Agent 基于文字与画面证据填写）\n\n"
    breakdown_md_content += "## 视频类型\n\n（待 Agent 判定；第一版优先 `talking-head` / `tutorial`，其他保守写 `mixed`）\n\n"
    breakdown_md_content += "## 叙事与结构\n\n（待 Agent 按语义合并段落，不按固定时间桶硬切）\n\n"
    breakdown_md_content += "## 视听语言\n\n（待 Agent 看过联系图和关键原始帧后填写；没有视觉证据时不得写具体视觉结论）\n\n"
    breakdown_md_content += "## 可借鉴点\n\n- （待 Agent 提炼：写清可借什么、为什么可借、什么不该借）\n\n"
    breakdown_md_content += "## 时间轴拆解\n\n| 时间 | 台词/字幕 | 画面变化 | 手法标签 |\n|---|---|---|---|\n| 待填写 | 待填写 | 待 Agent 看片后填写 | 待从封闭词表选择 |\n"

    breakdown_json_content = {
        "videoType": "",
        "oneLineThesis": "",
        "structure": [],
        "visualLanguage": {
            "camera": [],
            "editing": [],
            "subtitle": [],
            "ui": [],
        },
        "segments": [],
    }

    transcript_out.write_text(transcript_content, encoding="utf-8")
    meta_out.write_text(meta_content, encoding="utf-8")
    breakdown_md.write_text(breakdown_md_content, encoding="utf-8")
    breakdown_json.write_text(json.dumps(breakdown_json_content, ensure_ascii=False, indent=2), encoding="utf-8")


def write_workspace_readme(workspace: Path, manifest: Manifest):
    """在产物 workspace 根目录生成 README.md，指引用户先读什么。"""
    text_source = manifest.data.get("textEvidenceSource") or "unknown"
    source_label = {
        "platform-subtitles": "平台原生/自动字幕",
        "local-asr": "本地 ASR 兜底",
        "ocr": "帧内 OCR 兜底",
        "unknown": "未拿到文字证据",
    }.get(text_source, text_source)
    content = f"""# 拉片产物说明

本目录是 `507-video-pull` 的一次取证与拉片产物。所有脚本只负责确定性取证与模板填充，最终拉片结论由 agent 读取证据后填入。

## 推荐阅读顺序

1. **`meta.md`**：工作区状态、文字证据来源（本次为 `{text_source}` / {source_label}）、证据限制。
2. **`transcript.md`**：结构化后的台词/字幕文本人读版。
3. **`breakdown.md`**：拉片结论人读版——主旨、叙事结构、视听语言、可借鉴点、时间轴拆解。
4. **`breakdown.json`**：拉片结论机器版，供 `507-video-remake` 消费。

## 证据位置

- `raw/manifest.json`：取证步骤状态与失败原因。
- `raw/windows.jsonl`：分析层小窗原始记录（给 agent 看，不给人看）。
- `raw/subtitles/`、`raw/asr/`、`raw/ocr/`：各降级链路的文字证据，按需查。
- `raw/frames_uniform/`：1fps 抽帧（全局节奏）。
- `raw/frames_scenecut/`：场景切换抽帧（关键转折点）。
- `raw/contact_sheets/`：联系图汇总（看节奏、字幕、UI、镜头变化）。
- `raw/video/`：原始视频与平台字幕文件（如有）。

## 标签术语速查

`breakdown.md` / `breakdown.json` 中的英文标签对应中文含义（完整版见 `references/tag-vocabulary.md`）：

**叙事与结构（写入 `segments[].patterns`）**
- `hook-result-first`：结果先行开场，开场先抛结论/数据，再补过程。
- `hook-problem-first`：痛点先行开场，开场先抛问题或痛点。
- `problem-solution-demo`：问题—方案—演示推进结构。
- `listicle-step-flow`：列表/步骤顺序推进。
- `cta-comment-close`：结尾以评论/互动号召收束。

**镜头（写入 `segments[].techniques` 与 `visualLanguage.camera`）**
- `fixed-medium-close`：固定机位中近景。
- `single-background`：单一不变背景。
- `single-speaker-center`：单人主体稳定居中。

**剪辑（写入 `segments[].techniques` 与 `visualLanguage.editing`）**
- `hard-cut`：硬切，场景间不淡入淡出、直接跳切。
- `beat-paced-reveal`：信息节拍逐步揭示。
- `overlay-on-mention`：讲到具体概念时弹出对应画面。
- `return-to-speaker`：讲抽象思路时回到主讲人纯画面。

**字幕（写入 `segments[].techniques` 与 `visualLanguage.subtitle`）**
- `subtitle-bottom-bar`：底部字幕条。
- `subtitle-green-keyword`：字幕关键词绿色高亮。
- `keyword-memory-anchor`：关键词做记忆锚点。

**界面（写入 `segments[].techniques` 与 `visualLanguage.ui`）**
- `ui-overlay-card`：画面叠加 UI 卡片/截图。
- `topic-label-top-left`：左上角主题/系列标签。

## 下一步

- 需要重看拉片结论：直接编辑 `breakdown.md` 与 `breakdown.json`。
- 需要作为输入进入 `507-video-remake`：`video_remake.py run --pull-dir {workspace} --output-dir works/<选题slug>/视频 --project-name ... --theme ... --platform ... --duration ... --style ...`（创作包归宿作品主轴）。
- 需要重新跑取证：`video_pull.py run --video <url-or-path> --output-dir <parent> --force`。

## 重要限制

- 拉片结论中引用的具体台词、视觉判断必须能在上面证据文件中追溯到。
- 文字证据如有错别字（ASR/OCR 误差），以看到为准后可手动修订 `breakdown.md` 并同步更新 `breakdown.json`。
"""
    (workspace / "README.md").write_text(content, encoding="utf-8")


def run_pipeline(args):
    base_dir = Path(args.output_dir).expanduser().resolve()
    ensure_dir(base_dir)
    workspace = build_workspace(base_dir, args.video, args.title_hint, args.force)
    manifest = Manifest(workspace)
    manifest.update("videoInput", args.video)
    manifest.update("lang", args.lang or "auto")

    try:
        video_path = download_or_copy_video(args.video, manifest)
        manifest.update("videoPath", str(video_path))

        uniform_dir = manifest.raw_dir / "frames_uniform"
        scenecut_dir = manifest.raw_dir / "frames_scenecut"
        contact_dir = manifest.raw_dir / "contact_sheets"
        uniform_count = extract_frames(video_path, uniform_dir, "uniform")
        manifest.step("frames_uniform", StepResult("success", f"已完成 1fps 均匀抽帧，共 {uniform_count} 帧", str(uniform_dir)))
        scenecut_count = extract_frames(video_path, scenecut_dir, "scenecut")
        manifest.step("frames_scenecut", StepResult("success", f"已完成 scene-cut 抽帧，共 {scenecut_count} 帧", str(scenecut_dir)))
        sheets = make_contact_sheets(uniform_dir, contact_dir)
        manifest.step("contact_sheets", StepResult("success", f"已生成 {len(sheets)} 张联系图", str(contact_dir)))

        transcript_path = gather_platform_subtitles(manifest, args.lang)
        if transcript_path is None:
            transcript_path = extract_audio_asr(video_path, manifest, args.lang)
        if transcript_path is None:
            transcript_path = maybe_ocr(manifest)
        if transcript_path is None:
            manifest.update("status", "failed")
            raise SystemExit("没有拿到任何文字证据：平台字幕 / 自动字幕 / ASR / OCR 全部失败")

        windows_path = create_windows_jsonl(manifest, transcript_path)
        manifest.step("windows", StepResult("success", "已生成小窗原始记录", str(windows_path)))

        write_analysis_templates(workspace, transcript_path, manifest)
        manifest.step("templates", StepResult("success", "已生成 meta/transcript/breakdown 模板", str(workspace)))

        write_workspace_readme(workspace, manifest)
        manifest.step("workspace_readme", StepResult("success", "已生成产物 README", str(workspace / "README.md")))

        manifest.update("status", "success")
        print(json.dumps({
            "workspace": str(workspace),
            "manifest": str(manifest.path),
            "textEvidenceSource": manifest.data.get("textEvidenceSource"),
            "transcriptCandidate": str(transcript_path),
        }, ensure_ascii=False, indent=2))
    except Exception as exc:
        manifest.update("status", "failed")
        manifest.note(str(exc))
        raise


def normalize_subtitles_cli(args):
    segments = load_segments_from_file(Path(args.subtitle_path))
    if not segments:
        raise SystemExit("未从字幕文件解析出有效内容")
    out = Path(args.output_path)
    ensure_dir(out.parent)
    write_transcript_segments(segments, out)
    print(out)


def main():
    parser = argparse.ArgumentParser(description="507 Video Pull 取证脚本")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("check", help="检查本地依赖")

    run_parser = subparsers.add_parser("run", help="执行单视频取证链路")
    run_parser.add_argument("--video", required=True, help="视频 URL 或本地路径")
    run_parser.add_argument("--output-dir", default="./video-pull", help="输出根目录")
    run_parser.add_argument("--title-hint", help="可选标题提示，用于生成工作区名")
    run_parser.add_argument("--lang", help="字幕/ASR 语言，默认自动")
    run_parser.add_argument("--force", action="store_true", help="显式覆盖已有工作区")

    normalize_parser = subparsers.add_parser("normalize-subs", help="把字幕文件标准化为 transcript.txt")
    normalize_parser.add_argument("--subtitle-path", required=True)
    normalize_parser.add_argument("--output-path", required=True)

    args = parser.parse_args()
    if args.command == "check":
        raise SystemExit(check_env())
    if args.command == "run":
        run_pipeline(args)
        return
    if args.command == "normalize-subs":
        normalize_subtitles_cli(args)
        return
    parser.print_help()


if __name__ == "__main__":
    main()
