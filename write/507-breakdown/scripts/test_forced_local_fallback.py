#!/usr/bin/env python3
"""Regression: --force-local-fallback skips M3 understanding but still requires image key."""
from __future__ import annotations
import json, os, subprocess, sys, tempfile
from pathlib import Path
S=Path(__file__).resolve().parent
ws=Path(tempfile.mkdtemp(prefix="video-fallback-"))
(fake_modules:=ws/"fake-modules").mkdir()
(fake_modules/"faster_whisper.py").write_text("""\
from types import SimpleNamespace
class WhisperModel:
    def __init__(self, *args, **kwargs): pass
    def transcribe(self, *args, **kwargs):
        return [SimpleNamespace(start=0.0, end=1.0, text='synthetic transcript')], SimpleNamespace()
""",encoding="utf-8")
(video:=Path(f"{ws}_input.mp4")).parent.mkdir(parents=True,exist_ok=True)
subprocess.run(["ffmpeg","-y","-f","lavfi","-i","color=c=red:s=320x240:d=4","-f","lavfi","-i","color=c=blue:s=320x240:d=4","-f","lavfi","-i","sine=frequency=440:duration=8","-filter_complex","[0:v][1:v]concat=n=2:v=1[v]","-map","[v]","-map","2:a","-c:v","libx264","-c:a","aac","-shortest",str(video)],check=True,capture_output=True)
env={**os.environ,"MiniMax_API_KEY":"","PYTHONPATH":str(fake_modules)+os.pathsep+os.environ.get("PYTHONPATH","")}
r=subprocess.run([sys.executable,str(S/"video_pull.py"),"run","--video",str(video),"--output-dir",str(ws),"--title-hint","fb","--asr-python",sys.executable,"--force-local-fallback"],capture_output=True,text=True,env=env)
assert r.returncode!=0,(r.stdout+r.stderr)[-500:]
candidate=next(ws.glob(".video-pull-candidate-*/fb"))
manifest_path=candidate/"raw/video_manifest.json"
manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
assert manifest.get("analysisMode")=="forced_local_fallback",manifest
assert manifest.get("status")!="video_completed"
steps={name:item.get("status") for name,item in (manifest.get("steps") or {}).items()}
assert steps.get("video_asr")=="success",steps
assert steps.get("video_scene_cut")=="success",steps
assert (candidate/"analysis/video_adaptive_frames.json").is_file()
image=subprocess.run([sys.executable,str(S/"video_describe_key_frames.py"),"--workspace",str(candidate)],capture_output=True,text=True,env=env)
assert image.returncode!=0,image.stdout+image.stderr
assert "MiniMax_API_KEY 未导出" in image.stderr,image.stderr
print("PASS: forced-local-fallback skips M3, requires image key")
