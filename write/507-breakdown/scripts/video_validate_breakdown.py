#!/usr/bin/env python3
"""Final gate: validate the full breakdown schema, tags, evidence, and lifecycle."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from video_contract import ANALYSIS_DIR, STATUS_ANALYSIS_READY, STATUS_COMPLETED, VIDEO_BREAKDOWN_JSON, VIDEO_BREAKDOWN_MD, VIDEO_META, VIDEO_TRANSCRIPT, VideoManifest

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "assets" / "breakdown.schema.json").read_text(encoding="utf-8"))
VOCAB = ROOT / "references" / "tag-vocabulary.md"
VISUAL_GROUPS = ("camera", "editing", "subtitle", "ui")

def fail(message: str) -> None: raise SystemExit(message)
def tags() -> dict[str, set[str]]:
 groups: dict[str,set[str]]={}; current=None
 for line in VOCAB.read_text(encoding="utf-8").splitlines():
  heading=re.match(r"^##\s+([a-z]+)(?:/|\s|$)",line.strip())
  if heading: current=heading.group(1);groups.setdefault(current,set());continue
  item=re.match(r"^-\s+`([^`]+)`",line.strip())
  if item and current: groups[current].add(item.group(1))
 return groups
def seconds(value:str)->float:
 m=re.fullmatch(r"(\d{2}):(\d{2})(?::(\d{2}))?",value)
 if not m: raise ValueError(value)
 a,b,c=m.groups()
 if c is None:
  minutes, secs = int(a), int(b)
  if secs >= 60: raise ValueError(value)
  return minutes * 60 + secs
 hours, minutes, secs = int(a), int(b), int(c)
 if minutes >= 60 or secs >= 60: raise ValueError(value)
 return hours * 3600 + minutes * 60 + secs
def validate(data:dict)->None:
 required=set(SCHEMA["required"]); allowed=set(SCHEMA["properties"])
 if set(data)-allowed: fail(f"最终 JSON 存在非法字段：{sorted(set(data)-allowed)}")
 if required-set(data): fail(f"缺少必填字段：{sorted(required-set(data))}")
 if not isinstance(data["videoType"],str) or data["videoType"] not in SCHEMA["properties"]["videoType"]["enum"]: fail("非法 videoType")
 if not isinstance(data["oneLineThesis"],str) or not data["oneLineThesis"].strip(): fail("oneLineThesis 不能为空")
 if not isinstance(data["structure"],list) or not data["structure"]: fail("structure 必须为非空数组")
 if not isinstance(data["segments"],list) or not data["segments"]: fail("segments 必须为非空数组")
 g=tags(); structure_tags=g.get("structure",set()); technique_tags=set().union(*g.values())-structure_tags
 visual=data["visualLanguage"]
 if not isinstance(visual,dict) or set(visual) != set(VISUAL_GROUPS): fail("visualLanguage 必须包含且只包含四个标准分组")
 for group,items in visual.items():
  if not isinstance(items,list) or any(not isinstance(x,str) or x not in g.get(group,set()) for x in items): fail(f"visualLanguage.{group} 标签非法")
 for item in data["structure"]:
  if not isinstance(item,dict) or set(item)!={"label","summary"} or not all(isinstance(item[k],str) and item[k].strip() for k in item): fail("structure 项必须只有非空 label/summary")
 for seg in data["segments"]:
  fields={"start","end","transcript","visualChange","techniques","patterns"}
  if not isinstance(seg,dict) or set(seg)!=fields: fail("segment 字段非法")
  if not all(isinstance(seg[k],str) and seg[k].strip() for k in ("start","end","transcript","visualChange")): fail("segment 文本字段不能为空")
  try:
   if seconds(seg["end"]) <= seconds(seg["start"]): fail("segment 时间范围必须正向")
  except ValueError: fail("segment 时间格式必须为 MM:SS 或 HH:MM:SS")
  if not isinstance(seg["patterns"],list) or any(x not in structure_tags for x in seg["patterns"]): fail("segment patterns 标签非法")
  if not isinstance(seg["techniques"],list) or any(x not in technique_tags for x in seg["techniques"]): fail("segment techniques 标签非法")

def main()->int:
 p=argparse.ArgumentParser(description="校验 video_* 拉片包并完成状态");p.add_argument("--workspace",required=True);a=p.parse_args();ws=Path(a.workspace).expanduser().resolve();m=VideoManifest.load(ws)
 if m.data.get("status")!=STATUS_ANALYSIS_READY: fail(f"工作区未到 analysis_ready：{m.data.get('status')}")
 required=["video_localization","video_adaptive_frames","video_key_frame_images","video_analysis_brief"]
 if m.data.get("analysisMode")!="forced_local_fallback": required.insert(0,"video_understanding_minimax")
 for step in required:
  if m.data.get("steps",{}).get(step,{}).get("status")!="success": fail(f"前置阶段未成功：{step}")
 locations=ws/ANALYSIS_DIR/"video_locations.json"
 if not locations.exists(): fail("缺少定位结果：video_locations.json")
 units=json.loads(locations.read_text(encoding="utf-8")).get("semanticUnits",[])
 if not units: fail("定位结果缺少语义单元")
 understanding=ws/ANALYSIS_DIR/"video_understanding_minimax.json"
 if understanding.exists() and m.data.get("analysisMode")!="forced_local_fallback":
  ids=[u.get("id") for u in json.loads(understanding.read_text(encoding="utf-8")).get("semanticUnits",[])]
  if not ids or len(ids)!=len(set(ids)) or {u.get("id") for u in units}!=set(ids): fail("定位语义单元与 M3 输出不一致")
 def valid_window(w): return isinstance(w,dict) and isinstance(w.get("start"),(int,float)) and isinstance(w.get("end"),(int,float)) and w["end"]>w["start"] and isinstance(w.get("evidence"),str) and w["evidence"] in {"asr","ocr","image_visual_anchor"}
 invalid=[u.get("id") for u in units if u.get("localizationStatus") not in {"localized","unresolved"} or (u.get("localizationStatus")=="localized" and (not u.get("candidateWindows") or not all(valid_window(w) for w in u["candidateWindows"])))]
 unresolved=[u.get("id") for u in units if u.get("localizationStatus")=="unresolved" and (u.get("reference",{}).get("spokenAnchors") or u.get("reference",{}).get("visualAnchors"))]
 if invalid: fail(f"非法定位状态：{invalid}")
 if unresolved: fail(f"未核验的语义锚点：{unresolved}")
 for name in [VIDEO_META,VIDEO_TRANSCRIPT,VIDEO_BREAKDOWN_MD,VIDEO_BREAKDOWN_JSON]:
  path = ws / name
  if not path.exists(): fail(f"缺少最终产物：{name}")
  if not path.read_text(encoding="utf-8", errors="ignore").strip(): fail(f"最终产物为空：{name}")
 breakdown_md = (ws / VIDEO_BREAKDOWN_MD).read_text(encoding="utf-8", errors="ignore")
 if "待填写" in breakdown_md or "（待" in breakdown_md: fail("video_breakdown.md 仍含未填写模板")
 validate(json.loads((ws/VIDEO_BREAKDOWN_JSON).read_text(encoding="utf-8")))
 m.step("video_validation","success","最终拉片包校验通过",str(ws/VIDEO_BREAKDOWN_JSON));m.set_status(STATUS_COMPLETED)
 meta_path=ws/VIDEO_META
 if meta_path.exists():
  import re as _re
  text=meta_path.read_text(encoding="utf-8",errors="ignore")
  text=_re.sub(r"status: `[^`]+`","status: `video_completed`",text)
  meta_path.write_text(text,encoding="utf-8")
 print("video-validation-ok");return 0
if __name__=="__main__":raise SystemExit(main())
