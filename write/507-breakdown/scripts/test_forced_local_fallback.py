#!/usr/bin/env python3
"""Regression: --force-local-fallback skips M3 understanding but still requires image key."""
from __future__ import annotations
import json, os, subprocess, sys, tempfile
from pathlib import Path
S=Path(__file__).resolve().parent
ws=Path(tempfile.mkdtemp(prefix="video-fallback-"))
(video:=Path(f"{ws}_input.mp4")).parent.mkdir(parents=True,exist_ok=True)
subprocess.run(["ffmpeg","-y","-f","lavfi","-i","color=c=red:s=320x240:d=4","-f","lavfi","-i","color=c=blue:s=320x240:d=4","-f","lavfi","-i","sine=frequency=440:duration=8","-filter_complex","[0:v][1:v]concat=n=2:v=1[v]","-map","[v]","-map","2:a","-c:v","libx264","-c:a","aac","-shortest",str(video)],check=True,capture_output=True)
env={**os.environ,"MiniMax_API_KEY":""}
r=subprocess.run([sys.executable,str(S/"video_pull.py"),"run","--video",str(video),"--output-dir",str(ws),"--title-hint","fb","--force-local-fallback"],capture_output=True,text=True,env=env)
# image step must fail because key is empty
assert r.returncode!=0,(r.stdout+r.stderr)[-500:]
manifest=json.load(open(next(ws.glob("*/raw/video_manifest.json"))))
assert manifest.get("analysisMode")=="forced_local_fallback",manifest
assert manifest.get("status")!="video_completed"
print("PASS: forced-local-fallback skips M3, requires image key")
