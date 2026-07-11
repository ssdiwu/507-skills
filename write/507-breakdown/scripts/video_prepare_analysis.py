#!/usr/bin/env python3
"""Assemble evidence and unverified semantic references for the final agent pass."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from video_contract import ANALYSIS_DIR, VIDEO_BREAKDOWN_JSON, VIDEO_BREAKDOWN_MD, VIDEO_META, VIDEO_TRANSCRIPT, VideoManifest, ensure_dir

def main()->int:
 p=argparse.ArgumentParser(description="生成视频拉片分析简报");p.add_argument("--workspace",required=True);a=p.parse_args();ws=Path(a.workspace).expanduser().resolve();m=VideoManifest.load(ws);analysis=ws/ANALYSIS_DIR
 understanding=json.loads((analysis/"video_understanding_minimax.json").read_text(encoding="utf-8")) if (analysis/"video_understanding_minimax.json").exists() else {"semanticUnits":[]}
 locations=json.loads((analysis/"video_locations.json").read_text(encoding="utf-8"));observations=json.loads((analysis/"video_frame_observations.json").read_text(encoding="utf-8"))
 transcript_path=ws/"raw"/"video_asr"/"video_transcript.txt"
 if not transcript_path.exists(): transcript_path=ws/"raw"/"video_subtitles"/"video_transcript.txt"
 transcript=transcript_path.read_text(encoding="utf-8",errors="ignore") if transcript_path.exists() else "（无文字证据）"
 (ws/VIDEO_TRANSCRIPT).write_text("# Video Transcript\n\n"+transcript,encoding="utf-8")
 title = ws.name
 (ws/VIDEO_META).write_text(f"# Video Meta\n\n- `title`：{title}\n- status: `video_analysis_ready`\n- analysis_mode: `{m.data.get('analysisMode')}`\n- semantic_source: `{m.data.get('semanticSource')}`\n- manifest: `raw/video_manifest.json`\n",encoding="utf-8")
 (ws/VIDEO_BREAKDOWN_MD).write_text("# Video Breakdown\n\n> 最终结论必须由本地 ASR、OCR、PTS 帧和 scene-cut 证据核验；M3 时间与顺序仅为参考。\n\n## 一句话主旨\n\n（待填写）\n\n## 时间轴拆解\n\n（待填写）\n",encoding="utf-8")
 (ws/VIDEO_BREAKDOWN_JSON).write_text(json.dumps({"videoType":"","oneLineThesis":"","structure":[],"visualLanguage":{"camera":[],"editing":[],"subtitle":[],"ui":[]},"segments":[]},ensure_ascii=False,indent=2),encoding="utf-8")
 brief={"semanticReference":understanding,"localization":locations,"frameObservations":observations,"transcriptPath":str(transcript_path)}
 out=analysis/"video_analysis_brief.json";out.write_text(json.dumps(brief,ensure_ascii=False,indent=2),encoding="utf-8")
 (analysis/"video_analysis_brief.md").write_text("# Video Analysis Brief\n\n> M3 语义参考与本地证据索引；不直接等于最终拉片。\n\n```json\n"+json.dumps(brief,ensure_ascii=False,indent=2)+"\n```\n",encoding="utf-8")
 m.step("video_analysis_brief","success","已生成最终分析输入",str(out));m.set_status("video_analysis_ready");print(out);return 0
if __name__=="__main__":raise SystemExit(main())
