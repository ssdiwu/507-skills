#!/usr/bin/env python3
"""Bounded MiniMax image understanding for already-localized adaptive frames."""
from __future__ import annotations
import argparse,base64,json,mimetypes,os,re,subprocess
from pathlib import Path
from urllib.request import Request,urlopen
from video_contract import ANALYSIS_DIR, STATUS_VISUALLY_VERIFIED, VideoManifest, ensure_dir
from video_locate_segments import anchor_match

PROMPT="Return JSON only: {description:string, anchorChecks:[{anchor:string,visible:boolean,evidence:string}]}. Mark visible=true only for a clearly present anchor; false for absent, denied, quoted, uncertain, or unreadable anchors."
def describe(base:str,key:str,model:str,path:Path, anchors:list[str]=[])->dict:
    payload={"model":model,"max_tokens":1200,"messages":[{"role":"user","content":[{"type":"text","text":PROMPT+"\nTarget visual anchors: "+", ".join(anchors)+". State explicitly whether each is visible."},{"type":"image","source":{"type":"base64","media_type":mimetypes.guess_type(path.name)[0] or "image/jpeg","data":base64.b64encode(path.read_bytes()).decode()}}]}]}
    req=Request(base.rstrip("/")+"/anthropic/v1/messages",data=json.dumps(payload).encode(),headers={"Authorization":f"Bearer {key}","Content-Type":"application/json","anthropic-version":"2023-06-01"},method="POST")
    try:
        with urlopen(req,timeout=120) as r: data=json.loads(r.read().decode())
    except Exception as exc:
        detail=exc.read().decode("utf-8",errors="replace")[:500] if hasattr(exc,"read") else ""
        raise RuntimeError(f"图片理解请求失败：{exc} {detail}") from exc
    text="\n".join(x.get("text","") for x in data.get("content",[]) if x.get("type")=="text").strip()
    try: result=json.loads(text)
    except json.JSONDecodeError as exc: raise RuntimeError("图片理解未返回 JSON") from exc
    if not isinstance(result.get("description"),str) or not isinstance(result.get("anchorChecks"),list) or any(not isinstance(x,dict) or not isinstance(x.get("anchor"),str) or not x["anchor"].strip() or not isinstance(x.get("visible"),bool) or not isinstance(x.get("evidence"),str) or not x["evidence"].strip() for x in result["anchorChecks"]) or {x["anchor"] for x in result["anchorChecks"]} != set(anchors) or len(result["anchorChecks"]) != len(set(anchors)): raise RuntimeError("图片理解 JSON 字段非法")
    return result
def apply_visual_matches(ws:Path, items:list[dict], video:Path)->None:
    duration=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nk=1:nw=1",str(video)],text=True).strip())
    path=ws/ANALYSIS_DIR/"video_locations.json"
    data=json.loads(path.read_text(encoding="utf-8"))
    by_id={u.get("id"):u for u in data.get("semanticUnits",[])}
    for item in items:
        unit=by_id.get(item.get("semanticUnit"))
        anchors=(unit or {}).get("reference",{}).get("visualAnchors",[])
        checks={x.get("anchor"):x for x in item.get("anchorChecks",[]) if isinstance(x,dict)}
        if unit and anchors and all(checks.get(a,{}).get("visible") is True and not re.search(r"\b(?:not|no|hidden|invisible|fake|absent)\b|未|没有|不可见",checks.get(a,{}).get("evidence",""),re.I) for a in anchors):
            t=item["pts"]; unit["localizationStatus"]="localized"
            unit.setdefault("candidateWindows",[]).append({"start":max(0,t-0.5),"end":min(duration,t+0.5),"evidence":"image_visual_anchor","text":item["description"]})
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")

def main()->int:
    p=argparse.ArgumentParser(description="关键帧图片理解");p.add_argument("--workspace",required=True);p.add_argument("--model",default=os.getenv("MINIMAX_IMAGE_MODEL",os.getenv("MINIMAX_VIDEO_MODEL","MiniMax-M3")));p.add_argument("--max-frames",type=int,default=120);p.add_argument("--base-url",default=os.getenv("MINIMAX_API_BASE_URL","https://api.minimaxi.com"));a=p.parse_args()
    key=os.getenv("MiniMax_API_KEY");
    if not a.base_url.startswith("https://"): raise SystemExit("图片理解 base-url 必须为 HTTPS")
    if not key: raise SystemExit("MiniMax_API_KEY 未导出")
    ws=Path(a.workspace).expanduser().resolve();manifest=VideoManifest.load(ws); locations=json.loads((ws/ANALYSIS_DIR/"video_locations.json").read_text(encoding="utf-8")); anchors_by_id={u.get("id"):u.get("reference",{}).get("visualAnchors",[]) for u in locations.get("semanticUnits",[])};adaptive=json.loads((ws/ANALYSIS_DIR/"video_adaptive_frames.json").read_text(encoding="utf-8"));items=[]
    for window in adaptive.get("windows",[]):
        for frame in window.get("frames",[]):
            if len(items)>=a.max_frames:break
            path=(ws/frame["frame"]).resolve()
            if not path.is_relative_to(ws.resolve()): raise SystemExit("自适应帧路径越出工作区")
            result = describe(a.base_url,key,a.model,path,anchors_by_id.get(window.get("semanticUnit"),[]))
            description=result["description"]
            if not description:
                manifest.step("video_key_frame_images","failed",f"图片理解返回空描述：{frame['frame']}")
                raise SystemExit(f"图片理解返回空描述：{frame['frame']}")
            items.append({"pts":frame["pts"],"frame":frame["frame"],"semanticUnit":window.get("semanticUnit"),"description":description,"anchorChecks":result["anchorChecks"]})
        if len(items)>=a.max_frames:break
    if not items:
        manifest.step("video_key_frame_images","failed","没有可供图片理解的自适应关键帧")
        raise SystemExit("没有可供图片理解的自适应关键帧")
    apply_visual_matches(ws,items,Path(manifest.data["videoPath"]))
    locations=json.loads((ws/ANALYSIS_DIR/"video_locations.json").read_text(encoding="utf-8"))
    unresolved=[u.get("id") for u in locations.get("semanticUnits",[]) if u.get("localizationStatus")=="unresolved" and (u.get("reference",{}).get("visualAnchors") or u.get("reference",{}).get("spokenAnchors"))]
    if unresolved:
        manifest.step("video_key_frame_images","failed",f"视觉锚点未核验：{unresolved}")
        raise SystemExit(f"视觉锚点未核验：{unresolved}")
    out=ws/ANALYSIS_DIR/"video_frame_observations.json";ensure_dir(out.parent);out.write_text(json.dumps({"model":a.model,"observations":items,"limit":a.max_frames},ensure_ascii=False,indent=2),encoding="utf-8")
    manifest.step("video_key_frame_images","success","关键帧图片理解完成",str(out),model=a.model,frameCount=len(items),limit=a.max_frames)
    manifest.set_status(STATUS_VISUALLY_VERIFIED);print(out);return 0
if __name__=="__main__":raise SystemExit(main())
