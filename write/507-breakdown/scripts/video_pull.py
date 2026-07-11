#!/usr/bin/env python3
"""Public orchestrator for the required video breakdown lifecycle."""
from __future__ import annotations
import argparse,json,shutil,subprocess,sys
from pathlib import Path
from video_contract import (RAW_ASR_DIR,RAW_SCENECUT_DIR,RAW_VIDEO_DIR,STATUS_ACQUIRED,STATUS_ANALYSIS_READY,STATUS_SEMANTIC_FAILED,VideoManifest,ensure_dir,video_hash)

def slugify(value:str)->str:
 import re
 value=re.sub(r"[^a-z0-9\u4e00-\u9fff]+","-",value.lower()).strip("-");return value or "video"
def run(cmd:list[str]): return subprocess.run(cmd,check=True,capture_output=True,text=True)
def acquire(video:str,manifest:VideoManifest)->Path:
 out=manifest.raw_dir/RAW_VIDEO_DIR;ensure_dir(out)
 if video.startswith(("http://","https://")):
  template=str(out/"video.%(ext)s");run(["yt-dlp","-o",template,"--write-subs","--write-auto-subs","--sub-langs","all",video])
  files=[p for p in out.glob("video.*") if p.suffix.lower() not in {".json",".srt",".vtt",".ass",".lrc"}]
  if not files: raise RuntimeError("yt-dlp 未取得视频")
  return files[0]
 source=Path(video).expanduser().resolve()
 if not source.exists(): raise RuntimeError(f"本地视频不存在：{source}")
 dest=out/source.name;shutil.copy2(source,dest);return dest
def asr(video:Path,manifest:VideoManifest,lang:str|None)->None:
 out=manifest.raw_dir/RAW_ASR_DIR;ensure_dir(out);audio=out/"video_audio.wav";transcript=out/"video_transcript.txt"
 run(["ffmpeg","-y","-i",str(video),"-vn","-acodec","pcm_s16le","-ar","16000","-ac","1",str(audio)])
 python=Path.home()/".venvs"/"video-asr"/"bin"/"python"
 if not python.exists(): raise RuntimeError("未找到 ~/.venvs/video-asr/bin/python")
 run([str(python),str(Path(__file__).with_name("video_asr_faster_whisper.py")),str(audio),str(transcript),"--language",lang or "auto"])
 manifest.step("video_asr","success","本地 ASR 完成",str(transcript))
def scene_cut(video:Path,manifest:VideoManifest)->None:
 import re as _re
 out=manifest.raw_dir/RAW_SCENECUT_DIR;ensure_dir(out)
 pattern=str(out/"video_scene_%05d.jpg")
 result=subprocess.run(["ffmpeg","-y","-i",str(video),"-vf","select='gt(scene,0.25)',showinfo,scale=640:-1","-fps_mode","vfr",pattern],check=False,capture_output=True,text=True)
 frames=sorted(out.glob("video_scene_*.jpg"))
 if result.returncode != 0 and not frames:
  manifest.step("video_scene_cut","failed",(result.stderr or "scene-cut failed")[:500],str(out)); raise RuntimeError("scene-cut 失败")
 pts_values=[float(m) for m in _re.findall(r"pts_time:(\d+\.?\d*)", result.stderr or "")]
 index=[]
 for i,frame in enumerate(frames):
  pts=pts_values[i] if i < len(pts_values) else 0.0
  index.append({"pts":round(pts,3),"frame":str(frame.relative_to(manifest.workspace))})
 analysis_dir=manifest.workspace/"analysis";ensure_dir(analysis_dir)
 idx_path=analysis_dir/"video_scene_cut_index.json"
 idx_path.write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding="utf-8")
 manifest.step("video_scene_cut","success",f"scene-cut 索引完成，共 {len(frames)} 帧（含 PTS）",str(idx_path))
def call(name:str,ws:Path,*extra:str)->None:
 run([sys.executable,str(Path(__file__).with_name(name)),"--workspace",str(ws),*extra])
def main()->int:
 p=argparse.ArgumentParser(description="507 视频拉片流水线")
 sub=p.add_subparsers(dest="command");r=sub.add_parser("run");r.add_argument("--video",required=True);r.add_argument("--output-dir",default="./05-视频拉片");r.add_argument("--title-hint");r.add_argument("--lang");r.add_argument("--force",action="store_true");r.add_argument("--force-local-fallback",action="store_true")
 sub.add_parser("check")
 a=p.parse_args()
 if a.command=="check":
  import os;print({"ffmpeg":shutil.which("ffmpeg") is not None,"yt_dlp":shutil.which("yt-dlp") is not None,"minimax_key":bool(os.getenv("MiniMax_API_KEY"))});return 0
 if a.command!="run":p.print_help();return 1
 root=Path(a.output_dir).expanduser().resolve();ws=root/slugify(a.title_hint or Path(a.video).stem)
 if ws.exists() and not a.force: raise SystemExit(f"工作区已存在：{ws}；使用 --force 覆盖")
 if ws.exists():shutil.rmtree(ws)
 ensure_dir(ws/"raw");m=VideoManifest(ws);m.data["videoInput"]=a.video;m.flush()
 try:
  video=acquire(a.video,m);m.data["videoPath"]=str(video);m.data["videoHash"]=video_hash(video);m.set_status(STATUS_ACQUIRED);m.step("video_acquisition","success","视频取得",str(video))
  asr(video,m,a.lang);scene_cut(video,m)
  if a.force_local_fallback:
   m.set_mode("forced_local_fallback","local_frames_asr",["未使用 MiniMax-M3 整段语义理解"])
  else:
   try: call("video_understand_minimax.py",ws)
   except Exception:
    m.set_status(STATUS_SEMANTIC_FAILED);raise
  call("video_locate_segments.py",ws);call("video_extract_adaptive_frames.py",ws);call("video_describe_key_frames.py",ws);call("video_prepare_analysis.py",ws)
  print(ws)
 except Exception as exc:
  if m.data.get("status")!=STATUS_SEMANTIC_FAILED:m.set_status("failed")
  m.note(str(exc));raise
 return 0
if __name__=="__main__":raise SystemExit(main())
