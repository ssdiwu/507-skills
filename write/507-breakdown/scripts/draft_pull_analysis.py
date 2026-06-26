#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore").strip() if path.exists() else ""


def choose_transcript_path(workspace: Path, manifest: dict) -> Path | None:
    source = manifest.get("textEvidenceSource")
    ordered_candidates: list[Path] = []
    source_paths = {
        "platform-subtitles": workspace / "raw" / "subtitles" / "transcript.txt",
        "local-asr": workspace / "raw" / "asr" / "transcript.txt",
        "ocr": workspace / "raw" / "ocr" / "transcript.txt",
    }
    if source in source_paths:
        ordered_candidates.append(source_paths[source])
    ordered_candidates.extend(path for path in source_paths.values() if path not in ordered_candidates)
    for path in ordered_candidates:
        if load_text(path):
            return path
    return None


def load_windows(workspace: Path) -> list[dict]:
    windows_path = workspace / "raw" / "windows.jsonl"
    if not windows_path.exists():
        return []
    windows: list[dict] = []
    for line in windows_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip():
            continue
        windows.append(json.loads(line))
    return windows


def transcript_lines(path: Path | None) -> list[str]:
    if not path:
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip()]


def collect_evidence(workspace: Path) -> dict:
    contact_sheets = sorted((workspace / "raw" / "contact_sheets").glob("*.jpg"))
    uniform_frames = sorted((workspace / "raw" / "frames_uniform").glob("*.jpg"))
    scenecut_frames = sorted((workspace / "raw" / "frames_scenecut").glob("*.jpg"))
    return {
        "contactSheets": [str(path) for path in contact_sheets],
        "uniformFrameCount": len(uniform_frames),
        "sceneCutFrameCount": len(scenecut_frames),
    }


def write_evidence_templates(workspace: Path, manifest: dict, lines: list[str], windows: list[dict], evidence: dict):
    title = manifest.get("titleHint") or workspace.name
    source = manifest.get("textEvidenceSource") or "unknown"

    meta_content = "# Meta\n\n"
    meta_content += f"- `title`：{title}\n"
    meta_content += "- `video_type`：待 Agent 基于文字与画面证据判定\n"
    meta_content += "- `status`：evidence-ready\n"
    meta_content += f"- `text_evidence_source`：`{source}`\n"
    meta_content += f"- `workspace`：`{workspace}`\n"
    meta_content += f"- `manifest`：`{workspace / 'raw' / 'manifest.json'}`\n"
    meta_content += f"- `contact_sheets`：{len(evidence['contactSheets'])} 张\n"
    meta_content += f"- `uniform_frames`：{evidence['uniformFrameCount']} 帧\n"
    meta_content += f"- `scene_cut_frames`：{evidence['sceneCutFrameCount']} 帧\n"

    transcript_content = "# Transcript\n\n"
    transcript_content += f"- 文字来源：`{source}`\n\n"
    transcript_content += "## 原始文字\n\n"
    transcript_content += "\n".join(lines) if lines else "（暂无可用文字）"

    sample_windows = windows[:8]
    breakdown_md = [
        "# Breakdown",
        "",
        "> 这是证据摘要模板，不是最终拉片分析。Agent 必须读文字、看联系图、必要时回看关键原始帧后再填写具体视觉和叙事判断。",
        "",
        "## 一句话主旨",
        "",
        "（待 Agent 基于证据填写）",
        "",
        "## 视频类型",
        "",
        "（待 Agent 判定）",
        "",
        "## 叙事与结构",
        "",
        "（待 Agent 按语义合并填写，不按固定时间桶硬切）",
        "",
        "## 视听语言",
        "",
        "（待 Agent 看过 `raw/contact_sheets/` 与必要原始帧后填写；无证据不写具体视觉标签）",
        "",
        "## 可借鉴点",
        "",
        "- （待 Agent 写清可借什么、为什么可借、什么不该借）",
        "",
        "## 证据小窗预览",
        "",
        "| 时间 | 文字来源 | 文字 |",
        "|---|---|---|",
    ]
    if sample_windows:
        for window in sample_windows:
            text = re.sub(r"\s+", " ", str(window.get("text", ""))).strip()
            breakdown_md.append(f"| {window.get('start', '')}-{window.get('end', '')} | `{window.get('source', source)}` | {text} |")
    else:
        breakdown_md.append("| 待生成 | 待生成 | 待生成 |")
    breakdown_md.extend([
        "",
        "## 时间轴拆解",
        "",
        "| 时间 | 台词/字幕 | 画面变化 | 手法标签 |",
        "|---|---|---|---|",
        "| 待填写 | 待填写 | 待 Agent 看片后填写 | 待从封闭词表选择 |",
    ])

    breakdown_json = {
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

    (workspace / "meta.md").write_text(meta_content, encoding="utf-8")
    (workspace / "transcript.md").write_text(transcript_content, encoding="utf-8")
    (workspace / "breakdown.md").write_text("\n".join(breakdown_md), encoding="utf-8")
    (workspace / "breakdown.json").write_text(json.dumps(breakdown_json, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh evidence-based analysis templates without semantic or visual conclusions")
    parser.add_argument("--workspace", required=True)
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser().resolve()
    manifest = json.loads((workspace / "raw" / "manifest.json").read_text(encoding="utf-8"))
    transcript_path = choose_transcript_path(workspace, manifest)
    write_evidence_templates(
        workspace,
        manifest,
        transcript_lines(transcript_path),
        load_windows(workspace),
        collect_evidence(workspace),
    )
    print(workspace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
