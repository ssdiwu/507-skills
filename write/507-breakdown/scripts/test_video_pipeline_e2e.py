#!/usr/bin/env python3
"""End-to-end default breakdown → validation → remix test.

Requires MiniMax_API_KEY. Generates a 6-second red-to-blue video locally,
runs the mandatory M3 pipeline, fills a minimal evidence-backed breakdown,
validates it to video_completed, then verifies remix consumes the new contract.
"""
from __future__ import annotations
import json, os, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BREAKDOWN = ROOT / "507-breakdown" / "scripts"
REMIX = ROOT / "507-remix" / "scripts" / "video_remake.py"

def run(cmd): subprocess.run(cmd, check=True)
def main():
 if not os.getenv("MiniMax_API_KEY"): raise SystemExit("MiniMax_API_KEY is required")
 root=Path(tempfile.mkdtemp(prefix="video-breakdown-e2e-")); video=root/"video.mp4"; pull=root/"pull"; remix=root/"remix"
 run(["ffmpeg","-y","-f","lavfi","-i","color=c=red:s=320x240:d=3","-f","lavfi","-i","color=c=blue:s=320x240:d=3","-f","lavfi","-i","sine=frequency=440:duration=6","-filter_complex","[0:v][1:v]concat=n=2:v=1[v]","-map","[v]","-map","2:a","-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-shortest",str(video)])
 run([sys.executable,str(BREAKDOWN/"video_pull.py"),"run","--video",str(video),"--output-dir",str(pull),"--title-hint","e2e"])
 ws=pull/"e2e"
 breakdown={"videoType":"tutorial","oneLineThesis":"红蓝场景切换验证。","structure":[{"label":"hook","summary":"红转蓝。"}],"visualLanguage":{"camera":[],"editing":["hard-cut"],"subtitle":[],"ui":[]},"segments":[{"start":"00:03","end":"00:05","transcript":"测试音轨","visualChange":"红切蓝","techniques":["hard-cut"],"patterns":["hook-result-first"]}]}
 (ws/"video_breakdown.json").write_text(json.dumps(breakdown,ensure_ascii=False,indent=2),encoding="utf-8")
 (ws/"video_breakdown.md").write_text("# Video Breakdown\n\n## 一句话主旨\n\n红蓝场景切换验证。\n",encoding="utf-8")
 run([sys.executable,str(BREAKDOWN/"video_validate_breakdown.py"),"--workspace",str(ws)])
 assert json.loads((ws/"raw"/"video_manifest.json").read_text())["status"]=="video_completed"
 run([sys.executable,str(REMIX),"run","--pull-dir",str(ws),"--project-name","e2e","--theme","test","--platform","test","--duration","6s","--style","minimal","--output-dir",str(remix)])
 assert (remix/"e2e"/"prompt-pack.json").exists()
 print("PASS: default M3 pipeline → video_completed → remix")
if __name__=="__main__": main()
