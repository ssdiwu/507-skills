#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,shutil
p=argparse.ArgumentParser();p.add_argument('--carrier',choices=('html','pptx'));p.add_argument('--simulate-missing-officecli',action='store_true');p.add_argument('--simulate-missing-browser',action='store_true');p.add_argument('--simulate-missing-webgl',action='store_true');p.add_argument('--simulate-missing-asset',action='store_true');a=p.parse_args()
office=False if a.simulate_missing_officecli else bool(shutil.which('officecli'))
browser=False if a.simulate_missing_browser else bool(shutil.which('google-chrome') or shutil.which('chromium') or (__import__('os').environ.get('CHROME_PATH') and __import__('os').access(__import__('os').environ['CHROME_PATH'],__import__('os').X_OK)))
asset_ok=not a.simulate_missing_asset
if a.carrier=='pptx' and not office: out={'status':'blocked','carrier':'pptx','reason':'officecli unavailable'}
elif a.carrier=='pptx' and not asset_ok: out={'status':'blocked','carrier':'pptx','reason':'asset unavailable'}
elif a.carrier=='html' and not asset_ok: out={'status':'fallback','carrier':'html','reason':'asset unavailable; use semantic fallback'}
elif a.carrier: out={'status':'ready','carrier':a.carrier,'reason':'explicit choice'}
elif office and asset_ok: out={'status':'ready','carrier':'pptx','reason':'officecli probe'}
else: out={'status':'fallback','carrier':'html','reason':'officecli or asset unavailable'}
out.update(officecli=office,installAttempted=False,browser='missing-static-html-only' if not browser else 'available',webgl='missing-css-fallback' if a.simulate_missing_webgl else 'available',asset='missing-blocked' if not asset_ok else 'available')
print(json.dumps(out,ensure_ascii=False))
