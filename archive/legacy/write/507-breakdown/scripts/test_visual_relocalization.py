#!/usr/bin/env python3
import json,sys,tempfile,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from video_describe_key_frames import apply_visual_matches
ws=Path(tempfile.mkdtemp());(ws/'analysis').mkdir();video=ws/'input.mp4';subprocess.run(['ffmpeg','-y','-f','lavfi','-i','color=c=blue:s=16x16:d=4','-c:v','libx264',str(video)],check=True,capture_output=True)
p=ws/'analysis/video_locations.json';p.write_text(json.dumps({'semanticUnits':[{'id':'u','localizationStatus':'unresolved','candidateWindows':[],'reference':{'visualAnchors':['blue screen']}}]}))
apply_visual_matches(ws,[{'semanticUnit':'u','pts':3.0,'description':'A blue screen fills the frame.','anchorChecks':[{'anchor':'blue screen','visible':True,'evidence':'The blue screen is clearly visible.'}]}],video)
u=json.loads(p.read_text())['semanticUnits'][0];assert u['localizationStatus']=='localized' and u['candidateWindows'][0]['evidence']=='image_visual_anchor'
p.write_text(json.dumps({'semanticUnits':[{'id':'u','localizationStatus':'unresolved','candidateWindows':[],'reference':{'visualAnchors':['blue screen']}}]}))
apply_visual_matches(ws,[{'semanticUnit':'u','pts':3.0,'description':'The blue screen is NOT visible.','anchorChecks':[{'anchor':'blue screen','visible':False,'evidence':'The blue screen is not visible.'}]}],video)
assert json.loads(p.read_text())['semanticUnits'][0]['localizationStatus']=='unresolved'
p.write_text(json.dumps({'semanticUnits':[{'id':'u','localizationStatus':'unresolved','candidateWindows':[],'reference':{'visualAnchors':['no text']}}]}))
apply_visual_matches(ws,[{'semanticUnit':'u','pts':3.0,'description':'The frame contains no lettering.','anchorChecks':[{'anchor':'no text','visible':True,'evidence':'No letters or characters are present anywhere in the frame.'}]}],video)
assert json.loads(p.read_text())['semanticUnits'][0]['localizationStatus']=='localized'
print('PASS: visual anchor rematches only affirmative image evidence')
