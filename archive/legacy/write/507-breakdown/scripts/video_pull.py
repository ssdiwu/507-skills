#!/usr/bin/env python3
"""Public orchestrator for the required video breakdown lifecycle."""
from __future__ import annotations
import argparse,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
from video_contract import (RAW_ASR_DIR,RAW_SCENECUT_DIR,RAW_VIDEO_DIR,STATUS_ACQUIRED,STATUS_ANALYSIS_READY,STATUS_COMPLETED,STATUS_FAILED,STATUS_SEMANTIC_FAILED,VideoManifest,ensure_dir,video_hash)

def slugify(value:str)->str:
 import re
 value=re.sub(r"[^a-z0-9\u4e00-\u9fff]+","-",value.lower()).strip("-");return value or "video"
def run(cmd:list[str]): return subprocess.run(cmd,check=True,capture_output=True,text=True)
def asr_python_candidate(explicit:str|None)->Path:
 raw=explicit or os.getenv("VIDEO_ASR_PYTHON") or sys.executable
 return Path(os.path.abspath(Path(raw).expanduser()))
def asr_python_available(python:Path)->bool:
 return python.is_file() and os.access(python,os.X_OK)
def python_has_module(python:Path,module:str)->bool:
 if not asr_python_available(python): return False
 try:return subprocess.run([str(python),"-c",f"import {module}"],check=False,capture_output=True,text=True).returncode==0
 except OSError:return False
def resolve_asr_python(explicit:str|None)->Path:
 python=asr_python_candidate(explicit)
 if not asr_python_available(python): raise RuntimeError(f"ASR Python 不可用：{python}；请用 --asr-python 或 VIDEO_ASR_PYTHON 指定可执行文件")
 return python
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
def asr(video:Path,manifest:VideoManifest,lang:str|None,asr_python:str|None)->None:
 out=manifest.raw_dir/RAW_ASR_DIR;ensure_dir(out);audio=out/"video_audio.wav";transcript=out/"video_transcript.txt"
 run(["ffmpeg","-y","-i",str(video),"-vn","-acodec","pcm_s16le","-ar","16000","-ac","1",str(audio)])
 python=resolve_asr_python(asr_python)
 if not python_has_module(python,"faster_whisper"): raise RuntimeError(f"ASR Python 未安装 faster-whisper：{python}")
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
def workspace_status(ws:Path)->str|None:
 path=ws/"raw"/"video_manifest.json"
 if not path.is_file():return None
 try:return json.loads(path.read_text(encoding="utf-8")).get("status")
 except (OSError,json.JSONDecodeError):return None
def remove_path(path:Path)->None:
 if path.is_dir() and not path.is_symlink():shutil.rmtree(path)
 else:path.unlink(missing_ok=True)
def promote_workspace(candidate:Path,target:Path)->None:
 backup_root=Path(tempfile.mkdtemp(prefix=".video-pull-backup-",dir=target.parent));backup=backup_root/target.name
 moved_old=False;installed=False
 try:
  if target.exists():os.replace(target,backup);moved_old=True
  os.replace(candidate,target);installed=True
 except BaseException as publish_error:
  try:
   if installed and target.exists():remove_path(target)
   if moved_old and backup.exists():os.replace(backup,target)
  except BaseException as rollback_error:
   raise RuntimeError(f"候选工作区发布失败且旧工作区恢复失败；备份保留在：{backup}") from rollback_error
  shutil.rmtree(backup_root,ignore_errors=True)
  raise publish_error
 shutil.rmtree(backup_root,ignore_errors=True)
def main()->int:
 p=argparse.ArgumentParser(description="视频拉片流水线")
 sub=p.add_subparsers(dest="command");r=sub.add_parser("run");r.add_argument("--video",required=True);r.add_argument("--output-dir",default="./05-视频拉片");r.add_argument("--title-hint");r.add_argument("--lang");r.add_argument("--asr-python",help="运行 faster-whisper 的 Python 可执行文件");r.add_argument("--force",action="store_true");r.add_argument("--force-local-fallback",action="store_true")
 c=sub.add_parser("check");c.add_argument("--asr-python",help="检查指定的 ASR Python 可执行文件")
 a=p.parse_args()
 if a.command=="check":
  python=asr_python_candidate(a.asr_python);available=asr_python_available(python)
  print({"ffmpeg":shutil.which("ffmpeg") is not None,"ffprobe":shutil.which("ffprobe") is not None,"yt_dlp":shutil.which("yt-dlp") is not None,"tesseract":shutil.which("tesseract") is not None,"asr_python":str(python),"asr_python_exists":available,"faster_whisper":python_has_module(python,"faster_whisper") if available else False,"minimax_key":bool(os.getenv("MiniMax_API_KEY"))});return 0
 if a.command!="run":p.print_help();return 1
 root=Path(a.output_dir).expanduser().resolve();root.mkdir(parents=True,exist_ok=True);ws=root/slugify(a.title_hint or Path(a.video).stem)
 if ws.exists() and not a.force: raise SystemExit(f"工作区已存在：{ws}；使用 --force 覆盖")
 if ws.exists() and workspace_status(ws)==STATUS_COMPLETED: raise SystemExit(f"工作区已是 video_completed，不能用 video_analysis_ready 候选覆盖：{ws}；请使用新的 --title-hint")
 candidate_parent=Path(tempfile.mkdtemp(prefix=".video-pull-candidate-",dir=root));candidate_ws=candidate_parent/ws.name
 ensure_dir(candidate_ws/"raw");m=VideoManifest(candidate_ws);m.data["videoInput"]=a.video;m.flush()
 if a.force_local_fallback:m.set_mode("forced_local_fallback","local_frames_asr",["未使用 MiniMax-M3 整段语义理解"])
 try:
  video=acquire(a.video,m);m.data["videoPath"]=m.workspace_ref(video);m.data["videoHash"]=video_hash(video);m.set_status(STATUS_ACQUIRED);m.step("video_acquisition","success","视频取得",str(video))
  asr(video,m,a.lang,a.asr_python);scene_cut(video,m)
  if not a.force_local_fallback:
   try: call("video_understand_minimax.py",candidate_ws)
   except Exception:
    m.set_status(STATUS_SEMANTIC_FAILED);raise
  call("video_locate_segments.py",candidate_ws);call("video_extract_adaptive_frames.py",candidate_ws);call("video_describe_key_frames.py",candidate_ws);call("video_prepare_analysis.py",candidate_ws)
  completed=VideoManifest.load(candidate_ws)
  if completed.data.get("status")!=STATUS_ANALYSIS_READY:raise RuntimeError(f"候选工作区未达到 {STATUS_ANALYSIS_READY}：{completed.data.get('status')}")
 except Exception as exc:
  if m.data.get("status")!=STATUS_SEMANTIC_FAILED:m.set_status(STATUS_FAILED)
  m.note(str(exc));print(f"候选工作区失败，旧工作区未改动；诊断证据保留在：{candidate_ws}",file=sys.stderr);raise
 promote_workspace(candidate_ws,ws);shutil.rmtree(candidate_parent,ignore_errors=True);print(ws)
 return 0
if __name__=="__main__":raise SystemExit(main())
