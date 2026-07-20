#!/usr/bin/env python3
import argparse
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('file',type=Path);a=p.parse_args();t=a.file.read_text()
for token in ['<canvas id="hero"','role="region"','aria-live="polite"','touchstart','wheel','prefers-reduced-motion','requestAnimationFrame','<main id="deck"','flex:0 0 100vw','.js #deck','quote-box','addEventListener(\'resize\',resize)']:
 if token not in t: raise SystemExit(f'missing {token}')
if 'http://' in t or 'https://' in t: raise SystemExit('remote resource found')
print('HTML static contract passed:',a.file)