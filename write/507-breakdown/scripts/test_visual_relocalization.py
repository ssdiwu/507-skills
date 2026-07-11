#!/usr/bin/env python3
import json,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from video_describe_key_frames import apply_visual_matches
ws=Path(tempfile.mkdtemp());(ws/'analysis').mkdir()
p=ws/'analysis/video_locations.json';p.write_text(json.dumps({'semanticUnits':[{'id':'u','localizationStatus':'unresolved','candidateWindows':[],'reference':{'visualAnchors':['blue screen']}}]}))
apply_visual_matches(ws,[{'semanticUnit':'u','pts':3.0,'description':'A blue screen fills the frame.'}])
u=json.loads(p.read_text())['semanticUnits'][0];assert u['localizationStatus']=='localized' and u['candidateWindows'][0]['evidence']=='image_visual_anchor'
print('PASS: visual anchor rematches to image-evidenced PTS window')
