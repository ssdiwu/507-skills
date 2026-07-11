#!/usr/bin/env python3
"""Extract bounded, PTS-labelled frames only for localized candidate windows."""
from __future__ import annotations
import argparse,json,subprocess
from pathlib import Path
from video_contract import ANALYSIS_DIR, RAW_ADAPTIVE_DIR, VideoManifest, ensure_dir

def extract(video:Path,out:Path,start:float,end:float,fps:float,budget:int)->list[dict]:
    frames=[]; t=start
    while t<=end and len(frames)<budget:
        path=out/f"video_frame_{int(t*1000):010d}.jpg"
        result = subprocess.run(["ffmpeg","-y","-ss",str(t),"-i",str(video),"-frames:v","1","-vf","scale=1280:-1","-q:v","2",str(path)],check=False,capture_output=True)
        if result.returncode == 0 and path.exists():
            frames.append({"pts":round(t,3),"frame":str(path)})
        t+=1/fps
    return frames

def main()->int:
    p=argparse.ArgumentParser(description="关键窗口自适应抽帧")
    p.add_argument("--workspace",required=True);p.add_argument("--fps",type=float,default=2);p.add_argument("--max-frames-per-window",type=int,default=40)
    a=p.parse_args()
    if a.fps<=0: raise SystemExit("--fps 必须为正数")
    if a.max_frames_per_window<=0: raise SystemExit("--max-frames-per-window 必须为正数")
    ws=Path(a.workspace).expanduser().resolve(); manifest=VideoManifest.load(ws); video=Path(manifest.data["videoPath"])
    locations=json.loads((ws/ANALYSIS_DIR/"video_locations.json").read_text(encoding="utf-8")); out_dir=ws/"raw"/RAW_ADAPTIVE_DIR;ensure_dir(out_dir)
    observations=[]; seen=set()
    for unit in locations.get("semanticUnits",[]):
        for window in unit.get("candidateWindows",[]):
            key=(round(window["start"],3),round(window["end"],3))
            if key in seen: continue
            seen.add(key); name=f"video_window_{int(key[0]*1000):010d}_{int(key[1]*1000):010d}"; target=out_dir/name;ensure_dir(target)
            frames=extract(video,target,key[0],key[1],a.fps,a.max_frames_per_window)
            observations.append({"semanticUnit":unit.get("id"),"window":window,"frames":[{"pts":f["pts"],"frame":str(Path(f["frame"]).relative_to(ws))} for f in frames],"budget":a.max_frames_per_window,"stopReason":"window_budget_or_end"})
    out=ws/ANALYSIS_DIR/"video_adaptive_frames.json";out.write_text(json.dumps({"fps":a.fps,"windows":observations},ensure_ascii=False,indent=2),encoding="utf-8")
    manifest.step("video_adaptive_frames","success","关键窗口自适应抽帧完成",str(out),fps=a.fps,maxFramesPerWindow=a.max_frames_per_window)
    print(out);return 0
if __name__=="__main__":raise SystemExit(main())
