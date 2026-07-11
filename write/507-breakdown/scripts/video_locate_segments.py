#!/usr/bin/env python3
"""Create a PTS-labelled 10-second locator index and evidence-backed windows."""
from __future__ import annotations
import argparse, json, re, shutil, subprocess, sys
from pathlib import Path
from video_contract import ANALYSIS_DIR, RAW_LOCATOR_DIR, STATUS_LOCALIZED, VideoManifest, ensure_dir

def duration(video: Path) -> float:
 return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nk=1:nw=1",str(video)],text=True).strip())
def anchor_match(anchor:str,text:str)->bool:
 anchor=anchor.strip().lower(); text=text.lower()
 if not anchor or re.search(r"\b(?:might|possibly|maybe|unclear|absent)\b|未出现|没有出现",text): return False
 if re.search(r"(?:not|no|without|absent|unclear|maybe|未|没有|不可见).{0,32}"+re.escape(anchor), text) or re.search(re.escape(anchor)+r".{0,32}(?:not\s+visible|not\s+shown|absent|unclear|maybe|不可见|没有)", text): return False
 if any(ord(c)>127 for c in anchor): return anchor in text
 return bool(re.search(r"(?<!\w)"+re.escape(anchor)+r"(?!\w)",text))
def transcript_hits(path:Path,anchors:list[str]):
 if not path.exists(): return []
 hits=[]
 for line in path.read_text(encoding="utf-8",errors="ignore").splitlines():
  m=re.match(r"\[(\d+):(\d+)-(\d+):(\d+)\]\s*(.*)",line)
  if m and any(anchor_match(x,m[5]) for x in anchors): hits.append((int(m[1])*60+int(m[2]),int(m[3])*60+int(m[4]),m[5]))
 return hits
def frame_at(video:Path,out:Path,t:float)->bool:
 r=subprocess.run(["ffmpeg","-y","-ss",str(t),"-i",str(video),"-frames:v","1","-vf","scale=640:-1","-q:v","3",str(out)],check=False,capture_output=True)
 return r.returncode==0 and out.exists()
def ocr_index(ws:Path,coarse:list[dict],manifest:VideoManifest):
 if not shutil.which("tesseract"):
  manifest.step("video_ocr","skipped","未安装 tesseract");return []
 d=ws/"raw"/"video_ocr";ensure_dir(d);helper=Path(__file__).with_name("video_ocr_tesseract.py");rows=[]
 for item in coarse:
  output=d/(Path(item["frame"]).stem+".txt");r=subprocess.run([sys.executable,str(helper),str(ws/item["frame"]),str(output)],capture_output=True,text=True)
  if r.returncode==0 and output.exists() and (text:=output.read_text(encoding="utf-8",errors="ignore").strip()): rows.append({"pts":item["pts"],"frame":item["frame"],"text":text})
 out=ws/ANALYSIS_DIR/"video_ocr_index.json";ensure_dir(out.parent);out.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8");manifest.step("video_ocr","success",f"定位 OCR 完成，共 {len(rows)} 条",str(out));return rows
def main():
 p=argparse.ArgumentParser(description="本地语义锚点定位");p.add_argument("--workspace",required=True);p.add_argument("--interval",type=float,default=10);a=p.parse_args();
 if a.interval<=0: raise SystemExit("--interval 必须为正数")
 ws=Path(a.workspace).expanduser().resolve();m=VideoManifest.load(ws);video=Path(m.data["videoPath"]);d=ws/"raw"/RAW_LOCATOR_DIR;ensure_dir(d);total=duration(video);coarse=[]
 for t in [round(i*a.interval,3) for i in range(int((max(total-0.001,0))//a.interval)+1)]:
  path=d/f"video_frame_{int(t*1000):010d}.jpg"
  if frame_at(video,path,t): coarse.append({"pts":t,"frame":str(path.relative_to(ws))})
 ocr=ocr_index(ws,coarse,m);u=ws/ANALYSIS_DIR/"video_understanding_minimax.json";understanding=json.loads(u.read_text(encoding="utf-8")) if u.exists() else {"semanticUnits":[{"id":"forced_local_scan","meaning":"全片本地降级视觉搜索","spokenAnchors":[],"visualAnchors":[]}]}
 transcript=ws/"raw"/"video_asr"/"video_transcript.txt";units=[]
 scene_cut_path=ws/"analysis"/"video_scene_cut_index.json"
 scene_cuts=json.loads(scene_cut_path.read_text(encoding="utf-8")) if scene_cut_path.exists() else []
 for unit in understanding.get("semanticUnits",[]):
  windows=[{"start":s,"end":e,"evidence":"asr","text":t} for s,e,t in transcript_hits(transcript,unit.get("spokenAnchors",[]))]
  if not windows:
   for row in ocr:
    if any(anchor_match(x,row["text"]) for x in unit.get("visualAnchors",[])): windows.append({"start":row["pts"],"end":min(total,row["pts"]+a.interval),"evidence":"ocr","text":row["text"]})
  localization_status="localized" if windows else "unresolved"
  # Scene cuts and coarse PTS frames are visual-search material, not semantic matches.
  visual_search=[] if windows else ([{"pts":x["pts"],"evidence":"scene_cut"} for x in scene_cuts] or [{"pts":x["pts"],"evidence":"locator_pts"} for x in coarse])
  units.append({"id":unit.get("id"),"meaning":unit.get("meaning"),"reference":unit,"localizationStatus":localization_status,"candidateWindows":windows,"visualSearchPoints":visual_search})
 out=ws/ANALYSIS_DIR/"video_locations.json";out.write_text(json.dumps({"locatorIntervalSec":a.interval,"coarseFrames":coarse,"ocrIndex":ocr,"semanticUnits":units},ensure_ascii=False,indent=2),encoding="utf-8");m.step("video_localization","success","已建立 10 秒定位索引和候选窗口",str(out),intervalSec=a.interval);m.set_status(STATUS_LOCALIZED);print(out)
if __name__=="__main__":main()
