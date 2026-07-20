#!/usr/bin/env python3
"""Render a mature slide-content package as one offline HTML deck."""
from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path

from design_system import DIRECTIONS, direction, validate_deck

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "scripts/fixtures/collaboration-baseline.json"


def text(value: object) -> str:
    return escape(str(value or ""))


def item_cards(items: list[dict]) -> str:
    return "".join(f'<article class="item"><h3>{text(item.get("label") or item.get("title"))}</h3><p>{text(item.get("body"))}</p></article>' for item in items)


def render_slide(slide: dict) -> str:
    kind = slide["kind"]
    if kind == "cover":
        body = f'<p class="eyebrow">{text(slide.get("eyebrow"))}</p><h1>{text(slide["title"])}</h1><p class="sub">{text(slide["subtitle"])}</p>'
    elif kind == "section":
        body = f'<p class="eyebrow">{text(slide.get("eyebrow"))}</p><h1>{text(slide["title"])}</h1><p class="sub">{text(slide["subtitle"])}</p>'
    elif kind == "image-text":
        asset = slide["asset"]
        body = f'<div class="split"><div><p class="eyebrow">{text(slide.get("eyebrow"))}</p><h2>{text(slide["title"])}</h2><p>{text(slide["body"])}</p></div><figure><div class="workbench" role="img" aria-label="{text(asset["alt"])}"><b>项目文件</b><b>编辑器</b><b>预览</b></div><figcaption>{text(slide.get("caption"))}</figcaption></figure></div>'
    elif kind in {"three-part", "process"}:
        body = f'<h2>{text(slide["title"])}</h2><div class="items {kind}">{item_cards(slide["items"])}</div>'
    elif kind == "comparison":
        body = f'<h2>{text(slide["title"])}</h2><div class="items comparison">{item_cards(slide["items"])}</div>'
    elif kind == "metric":
        body = f'<p class="eyebrow">关键数字</p><div class="metric">{text(slide["metric"])}</div><h2>{text(slide["title"])}</h2><p>{text(slide["body"])}</p>'
    else:
        body = f'<div class="quote-box">“<br><strong>{text(slide["quote"])}</strong><small>{text(slide["attribution"])}</small></div>'
    footer = f'<small class="footer">{text(slide["footer"])}</small>' if slide.get("footer") else ""
    label = slide.get("title") or slide.get("quote") or slide["id"]
    return f'<section class="slide {kind}" data-component="{kind}" id="{text(slide["id"])}" role="region" aria-label="{text(label)}">{body}{footer}</section>'


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--style", choices=DIRECTIONS, required=True)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    errors = validate_deck(data)
    if errors:
        raise SystemExit("invalid mature slide content:\n- " + "\n- ".join(errors))
    theme = direction(args.style)
    slides = data["slides"]
    cards = "".join(render_slide(slide) for slide in slides)
    html = """<!doctype html><html lang="__LANG__" data-direction="__DIRECTION__"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>__TITLE__ · __LABEL__</title><style>:root{--paper:#__PAPER__;--ink:#__INK__;--accent:#__ACCENT__;--title:__TITLE_FONT__;--radius:__RADIUS__;--density:__DENSITY__}*{box-sizing:border-box}body{margin:0;background:#151528;color:var(--ink);font-family:Arial,"PingFang SC",sans-serif}#deck{width:100%;transition:transform .55s ease}.js body{overflow:hidden}.js #deck{display:flex;width:100vw;height:100vh}.js .slide{flex:0 0 100vw;height:100vh;min-height:0}.static.js body{overflow:auto}.static.js #deck{display:block;width:auto;height:auto}.static.js .slide{display:block;width:auto;height:auto;min-height:100vh}.slide{min-height:100vh;padding:7vh 12vw;background:var(--paper);position:relative;overflow:hidden;z-index:2}h1,h2,h3{font-family:var(--title);margin:.2em 0}h1{font-size:clamp(3rem,7vw,7rem)}h2{font-size:clamp(2.2rem,4vw,4.5rem)}p{font-size:clamp(1.05rem,1.8vw,1.7rem);max-width:37rem;line-height:1.3}.eyebrow,h3{color:var(--accent)}.sub{font-size:clamp(1.4rem,2.3vw,2.4rem)}.split,.items{display:grid;gap:4vw}.split{grid-template-columns:1fr 1fr}.items{grid-template-columns:repeat(3,1fr);margin-top:8vh}.comparison{grid-template-columns:repeat(2,1fr)}.item{padding:1.6rem;border:2px solid var(--ink);border-radius:var(--radius)}.process .item{border-color:var(--accent)}h3{font-size:clamp(2rem,4vw,4rem)}.workbench{height:45vh;background:#202428;color:#eee;padding:3rem;display:flex;justify-content:space-between;border:8px solid #111;border-radius:var(--radius)}figcaption,small{display:block;margin-top:1rem;color:var(--accent)}.footer{position:absolute;left:12vw;bottom:2rem}.metric{font:clamp(7rem,22vw,19rem)/.8 var(--title);color:var(--accent);margin-top:6vh}.quote-box{background:var(--ink);color:var(--paper);position:absolute;inset:0;padding:20vh 15vw;font-size:7rem}.quote-box strong{font-family:var(--title);font-size:clamp(2.5rem,5vw,5.5rem);line-height:1.25}.quote-box small{color:var(--paper)}#hero{position:fixed;inset:0;pointer-events:none;opacity:.12;z-index:3;mix-blend-mode:multiply}.static #hero{display:none}.static #deck{transition:none}nav{position:fixed;right:2rem;bottom:1.5rem;z-index:3}button{font:inherit;margin:.2rem;padding:.5rem .8rem}@media(max-width:700px){.split,.items{grid-template-columns:1fr;gap:1rem}.slide{padding:8vh 8vw}.workbench{height:25vh}nav{left:.5rem;right:.5rem;display:flex;justify-content:flex-end;align-items:center}.footer{left:8vw;bottom:1rem}}@media(prefers-reduced-motion:reduce){#deck{transition:none}#hero{display:none}}</style><canvas id="hero" aria-hidden="true"></canvas><main id="deck">__CARDS__</main><nav aria-label="演示导航"><button id="prev">上一页</button><span id="status" aria-live="polite"></span><button id="next">下一页</button></nav><script>addEventListener('error',()=>{document.documentElement.classList.add('static');const d=document.querySelector('#deck');if(d)d.style.transform='none';document.querySelectorAll('.slide').forEach(s=>{s.setAttribute('aria-hidden','false');s.dataset.current='static'})},{once:true});const p=new URLSearchParams(location.search);if(p.has('fail-js'))throw new Error('intentional runtime failure');document.documentElement.classList.add('js');if(p.has('static')||p.has('reduced'))document.documentElement.classList.add('static');if(p.has('fail-init'))throw new Error('intentional initialization failure');const deck=document.querySelector('#deck'),slides=[...document.querySelectorAll('.slide')],status=document.querySelector('#status');let i=0;function go(n){i=Math.max(0,Math.min(slides.length-1,n));const stat=document.documentElement.classList.contains('static');deck.style.transform=stat?'none':`translateX(${-i*100}vw)`;status.textContent=`${i+1} / ${slides.length}`;slides.forEach((s,x)=>{s.setAttribute('aria-hidden',stat?'false':x===i?'false':'true');s.dataset.current=stat?'static':x===i?'true':'false'})}document.documentElement.dataset.motion=matchMedia('(prefers-reduced-motion: reduce)').matches?'reduced':'full';document.documentElement.dataset.responsive=slides.every(s=>s.getBoundingClientRect().width<=innerWidth+1)?'pass':'fail';document.documentElement.dataset.overflow=document.documentElement.scrollWidth<=innerWidth?'pass':'fail';go(Number(p.get('slide')||0));if(p.has('fail-after'))setTimeout(()=>{throw new Error('intentional post-navigation failure')},0);next.onclick=()=>go(i+1);prev.onclick=()=>go(i-1);addEventListener('keydown',e=>{if(['ArrowRight','PageDown',' '].includes(e.key))go(i+1);if(['ArrowLeft','PageUp'].includes(e.key))go(i-1)});let y;addEventListener('touchstart',e=>y=e.touches[0].clientY);addEventListener('touchend',e=>{if(y-e.changedTouches[0].clientY>40)go(i+1);if(e.changedTouches[0].clientY-y>40)go(i-1)});addEventListener('wheel',e=>{if(Math.abs(e.deltaY)>30)go(i+(e.deltaY>0?1:-1))},{passive:true});const c=document.querySelector('#hero'),x=p.has('no-webgl')?null:c.getContext('2d');if(!x){document.documentElement.classList.add('static');deck.style.transform='none';go(i);document.documentElement.dataset.overflow=document.documentElement.scrollWidth<=innerWidth?'pass':'fail'}function resize(){c.width=innerWidth;c.height=innerHeight}resize();addEventListener('resize',resize);function draw(t){if(!x)return;x.clearRect(0,0,c.width,c.height);for(let k=0;k<12;k++){x.fillStyle=getComputedStyle(document.documentElement).getPropertyValue('--accent');x.beginPath();x.arc((k/12*c.width+t/30)%c.width,c.height*.2+Math.sin(t/700+k)*80,120,0,7);x.fill()}if(!matchMedia('(prefers-reduced-motion: reduce)').matches&&!p.has('reduced'))requestAnimationFrame(draw)}if(x&&!p.has('static')&&!p.has('reduced'))requestAnimationFrame(draw);</script></html>"""
    replacements = {"__LANG__": text(data.get("language") or "zh-CN"), "__DIRECTION__": args.style, "__TITLE__": text(data["deck"]["title"]), "__LABEL__": text(theme["label"]), "__PAPER__": theme["paper"], "__INK__": theme["ink"], "__ACCENT__": theme["accent"], "__TITLE_FONT__": f'{theme["title_latin"]}, "{theme["title_ea"]}", serif', "__RADIUS__": theme["radius"], "__DENSITY__": theme["density"], "__CARDS__": cards}
    for marker, value in replacements.items():
        html = html.replace(marker, value)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()