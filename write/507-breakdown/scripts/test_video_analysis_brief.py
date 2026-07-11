#!/usr/bin/env python3
"""Regression: analysis brief requires successful non-empty image verification."""
from __future__ import annotations
import json, subprocess, sys, tempfile
from pathlib import Path
S=Path(__file__).resolve().parent;sys.path.insert(0,str(S))
from video_contract import VideoManifest

def workspace(ok:bool):
 ws=Path(tempfile.mkdtemp(prefix="video-brief-"));(ws/"raw"/"video_asr").mkdir(parents=True);(ws/"analysis").mkdir()
 m=VideoManifest(ws);m.data["videoPath"]="/tmp/input.mp4";m.flush()
 if ok:
  frame=ws/"raw"/"frame.jpg";frame.write_bytes(b"fixture")
  observations=[{"semanticUnit":"u","pts":1,"frame":"raw/frame.jpg","description":"verified frame"}]
 else: observations=[]
 for name,data in [("video_locations.json",{"semanticUnits":[{"id":"u"}]}),("video_frame_observations.json",{"observations":observations}),("video_adaptive_frames.json",{"windows":[{"semanticUnit":"u","frames":[{"pts":1,"frame":"raw/frame.jpg"}]}] if ok else []})]:(ws/"analysis"/name).write_text(json.dumps(data))
 (ws/"raw"/"video_asr"/"video_transcript.txt").write_text("[00:00-00:01] test")
 if ok:m.step("video_key_frame_images","success","verified")
 return ws
bad=workspace(False);r=subprocess.run([sys.executable,str(S/"video_prepare_analysis.py"),"--workspace",str(bad)],capture_output=True,text=True);assert r.returncode!=0
ok=workspace(True);subprocess.run([sys.executable,str(S/"video_prepare_analysis.py"),"--workspace",str(ok)],check=True)
m=json.loads((ok/"raw"/"video_manifest.json").read_text());assert m["status"]=="video_analysis_ready" and (ok/"analysis"/"video_analysis_brief.json").exists()
print("PASS: analysis brief rejects missing visual evidence and writes ready package after verification")
