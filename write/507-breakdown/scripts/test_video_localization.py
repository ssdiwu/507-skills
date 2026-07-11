#!/usr/bin/env python3
"""Local regression: 10-second PTS index and scene-cut-backed localization."""
from __future__ import annotations
import json, subprocess, sys, tempfile
from pathlib import Path
SCRIPTS=Path(__file__).resolve().parent; sys.path.insert(0,str(SCRIPTS))
from video_contract import VideoManifest, video_hash
from video_pull import scene_cut

root=Path(tempfile.mkdtemp(prefix="video-localization-")); video=root/"input.mp4"; ws=root/"workspace"
subprocess.run(["ffmpeg","-y","-f","lavfi","-i","color=c=red:s=320x240:d=6","-f","lavfi","-i","color=c=blue:s=320x240:d=6","-filter_complex","[0:v][1:v]concat=n=2:v=1[v]","-map","[v]","-c:v","libx264",str(video)],check=True,capture_output=True)
(ws/"raw"/"video_asr").mkdir(parents=True); (ws/"analysis").mkdir()
m=VideoManifest(ws); m.data["videoPath"]=str(video); m.data["videoHash"]=video_hash(video); m.flush()
(ws/"raw"/"video_asr"/"video_transcript.txt").write_text("",encoding="utf-8")
(ws/"analysis"/"video_understanding_minimax.json").write_text(json.dumps({"semanticUnits":[{"id":"u1","meaning":"cut","spokenAnchors":[],"visualAnchors":["unmatched"],"referencePosition":"unknown","referenceTimeHint":"unknown","status":"unlocalized"}]}),encoding="utf-8")
scene_cut(video,m)
subprocess.run([sys.executable,str(SCRIPTS/"video_locate_segments.py"),"--workspace",str(ws)],check=True)
data=json.loads((ws/"analysis"/"video_locations.json").read_text())
assert [x["pts"] for x in data["coarseFrames"]]==[0.0,10.0]
window=data["semanticUnits"][0]["candidateWindows"][0]
assert window["evidence"]=="scene_cut" and window["start"]>0
print("PASS: PTS locator index and scene-cut evidence window")
