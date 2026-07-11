#!/usr/bin/env python3
"""Local regression: localized windows have bounded PTS frames and stop reasons."""
from __future__ import annotations
import json, subprocess, sys, tempfile
from pathlib import Path
S=Path(__file__).resolve().parent; sys.path.insert(0,str(S))
from video_contract import VideoManifest, video_hash
root=Path(tempfile.mkdtemp(prefix="video-adaptive-")); video=root/"input.mp4"; ws=root/"workspace"
subprocess.run(["ffmpeg","-y","-f","lavfi","-i","testsrc2=s=320x240:d=4","-c:v","libx264",str(video)],check=True,capture_output=True)
(ws/"raw").mkdir(parents=True); (ws/"analysis").mkdir()
m=VideoManifest(ws);m.data["videoPath"]=str(video);m.data["videoHash"]=video_hash(video);m.flush()
(ws/"analysis"/"video_locations.json").write_text(json.dumps({"semanticUnits":[{"id":"u1","candidateWindows":[{"start":0,"end":3,"evidence":"scene_cut"}]}]}))
subprocess.run([sys.executable,str(S/"video_extract_adaptive_frames.py"),"--workspace",str(ws),"--fps","2","--max-frames-per-window","3"],check=True)
data=json.loads((ws/"analysis"/"video_adaptive_frames.json").read_text()); item=data["windows"][0]
assert len(item["frames"])==3 and item["budget"]==3 and item["stopReason"]=="frame_budget_reached"
assert [f["pts"] for f in item["frames"]]==[0,0.5,1.0]
print("PASS: bounded adaptive PTS frames record budget stop reason")
