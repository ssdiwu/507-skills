#!/usr/bin/env python3
"""Render content v3 + visual-plan v1 as one validated offline HTML deck."""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import subprocess
import sys
import tempfile
from html import escape
from pathlib import Path
from typing import Any

from design_system import PRESETS, language, normalize_deck, validate_deck
from text_layout import flow_classes, html_text
from visual_plan import load_plan, resolved_pages, validate_plan

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "scripts/fixtures/collaboration-baseline.json"


def text(value: object) -> str:
    return escape(str(value or ""))


def text_flow(visual: dict[str, Any], path: str) -> dict[str, Any] | None:
    value = (visual.get("textFlow") or {}).get(path)
    return value if isinstance(value, dict) else None


def heading(tag: str, value: object, visual: dict[str, Any], path: str, base: str = "") -> str:
    spec = text_flow(visual, path)
    classes = flow_classes(spec, base)
    class_attr = f' class="{classes}"' if classes else ""
    return f'<{tag}{class_attr} data-text-path="{text(path)}">{html_text(value, spec)}</{tag}>'


def item_cards(items: list[dict[str, Any]], visual: dict[str, Any], *, numbered: bool = False) -> str:
    cards: list[str] = []
    for offset, item in enumerate(items):
        number = f'<span class="item-number">{offset + 1:02d}</span>' if numbered else ""
        label_key = "label" if item.get("label") is not None else "title"
        label = heading("h3", item.get(label_key), visual, f"/items/{offset}/{label_key}")
        body = heading("p", item.get("body"), visual, f"/items/{offset}/body")
        cards.append(f'<article class="item">{number}{label}{body}</article>')
    return "".join(cards)


def asset_uri(asset: dict[str, Any], input_path: Path) -> str:
    raw = asset.get("path")
    if not isinstance(raw, str) or not raw:
        raise ValueError(f"asset {asset.get('id') or '<unknown>'} requires path")
    candidates = [(ROOT / raw).resolve(), (input_path.parent / raw).resolve()]
    source = next((candidate for candidate in candidates if candidate.is_file()), None)
    if source is None:
        raise FileNotFoundError(f"asset not found: {raw}")
    mime = mimetypes.guess_type(source.name)[0] or "application/octet-stream"
    return f"data:{mime};base64,{base64.b64encode(source.read_bytes()).decode('ascii')}"


def render_asset(asset: dict[str, Any], input_path: Path, visual: dict[str, Any], index: int) -> str:
    alt = text(asset.get("alt"))
    caption_key = "caption" if asset.get("caption") is not None else "label"
    caption = heading("figcaption", asset.get(caption_key), visual, f"/assets/{index}/{caption_key}")
    uri = asset_uri(asset, input_path)
    return f'<figure class="media-item"><img src="{uri}" alt="{alt}">{caption}</figure>'


def render_chart(slide: dict[str, Any], visual: dict[str, Any]) -> str:
    data = slide["data"]
    categories = data["categories"]
    series = data["series"]
    chart_type = data["chartType"]
    source = heading("small", data.get("source"), visual, "/data/source", "data-source") if data.get("source") else ""
    if chart_type == "line":
        values = [float(value) for item in series for value in item["values"]]
        low, high = min(values), max(values)
        span = high - low or 1
        polylines: list[str] = []
        for index, item in enumerate(series):
            points = " ".join(f"{8 + point * 84 / max(1, len(categories)-1):.2f},{86 - (float(value)-low) * 70/span:.2f}" for point, value in enumerate(item["values"]))
            polylines.append(f'<polyline class="series series-{index+1}" points="{points}" fill="none" vector-effect="non-scaling-stroke"/>')
        labels = "".join(heading("span", value, visual, f"/data/categories/{index}") for index, value in enumerate(categories))
        legend = "".join(f'<span><i class="series-{index+1}"></i>{heading("b", item["name"], visual, f"/data/series/{index}/name")}</span>' for index, item in enumerate(series))
        return f'<div class="chart chart-line" role="img" aria-label="{text(slide["title"])}"><svg viewBox="0 0 100 100" aria-hidden="true">{"".join(polylines)}</svg><div class="chart-labels">{labels}</div><div class="chart-legend">{legend}</div>{source}</div>'
    maximum = float((data.get("scale") or {}).get("max") or max(float(value) for item in series for value in item["values"]) or 1)
    rows: list[str] = []
    for category_index, category in enumerate(categories):
        tracks = "".join(
            f'<div class="bar-track" data-series="{series_index + 1}"><span class="bar series-{series_index+1}" style="--value:{float(item["values"][category_index])/maximum:.6f}">{heading("b", item["values"][category_index], visual, f"/data/series/{series_index}/values/{category_index}")}</span></div>'
            for series_index, item in enumerate(series)
        )
        category_label = heading("span", category, visual, f"/data/categories/{category_index}", "chart-category")
        rows.append(f'<div class="chart-row">{category_label}<div class="bar-group">{tracks}</div></div>')
    legend = "".join(f'<span><i class="series-{index+1}"></i>{heading("b", item["name"], visual, f"/data/series/{index}/name")}</span>' for index, item in enumerate(series))
    return f'<div class="chart chart-bars" role="img" aria-label="{text(slide["title"])}">{"".join(rows)}<div class="chart-legend">{legend}</div>{source}</div>'


def render_table(slide: dict[str, Any], visual: dict[str, Any]) -> str:
    data = slide["data"]
    head = "".join(heading("th", value, visual, f"/data/columns/{column}") for column, value in enumerate(data["columns"]))
    rows = "".join("<tr>" + "".join(heading("td", value, visual, f"/data/rows/{row_index}/{column}") for column, value in enumerate(row)) + "</tr>" for row_index, row in enumerate(data["rows"]))
    source = heading("small", data.get("source"), visual, "/data/source", "data-source") if data.get("source") else ""
    return f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>{source}</div>'


def render_slide(slide: dict[str, Any], visual: dict[str, Any], input_path: Path, base_language: str) -> str:
    component = slide["component"]
    presentation = visual["presentation"]
    treatment = visual.get("treatment", "default")
    theme = language(base_language, treatment)
    style = f'--slide-paper:#{theme["paper"]};--slide-ink:#{theme["ink"]};--slide-surface:#{theme["surface"]}'
    title = heading("h2", slide.get("title"), visual, "/title") if slide.get("title") else ""
    if component in {"cover", "section", "closing", "statement"}:
        title = heading("h1", slide["title"], visual, "/title")
        subtitle = heading("p", slide.get("subtitle") or slide.get("body"), visual, "/subtitle" if slide.get("subtitle") else "/body", "sub") if slide.get("subtitle") or slide.get("body") else ""
        cta = heading("strong", slide.get("cta"), visual, "/cta", "cta") if slide.get("cta") else ""
        eyebrow = heading("p", slide.get("eyebrow"), visual, "/eyebrow", "eyebrow") if slide.get("eyebrow") else ""
        body = f'<div class="hero-copy">{eyebrow}{title}{subtitle}{cta}</div>'
    elif component in {"collection", "comparison", "sequence"}:
        body = f'{title}<div class="items items-{component}">{item_cards(slide["items"], visual, numbered=component=="sequence")}</div>'
    elif component == "relationship":
        nodes = "".join(f'<article class="node" data-node="{text(node.get("id"))}">{heading("strong", node.get("label"), visual, f"/nodes/{index}/label")}{heading("span", node.get("body"), visual, f"/nodes/{index}/body")}</article>' for index, node in enumerate(slide["nodes"]))
        edges = "".join(f'<li>{heading("b", edge.get("from"), visual, f"/edges/{index}/from")} → {heading("b", edge.get("to"), visual, f"/edges/{index}/to")}{heading("span", edge.get("label"), visual, f"/edges/{index}/label")}</li>' for index, edge in enumerate(slide["edges"]))
        body = f'{title}<div class="relationship"><div class="nodes">{nodes}</div><ol class="edges">{edges}</ol></div>'
    elif component == "media-evidence":
        media = "".join(render_asset(asset, input_path, visual, index) for index, asset in enumerate(slide["assets"]))
        eyebrow = heading("p", slide.get("eyebrow"), visual, "/eyebrow", "eyebrow") if slide.get("eyebrow") else ""
        body_text = heading("p", slide.get("body"), visual, "/body") if slide.get("body") else ""
        body = f'<div class="split"><div>{eyebrow}{title}{body_text}</div><div class="media-grid media-count-{len(slide["assets"])}">{media}</div></div>'
    elif component == "quote":
        quote = heading("strong", slide["quote"], visual, "/quote")
        attribution = heading("cite", slide["attribution"], visual, "/attribution")
        body = f'<blockquote>“{quote}{attribution}</blockquote>'
    elif component == "metric":
        data = slide["data"]
        value = heading("strong", data["value"], visual, "/data/value")
        label_text = heading("span", data["label"], visual, "/data/label")
        context = heading("p", data.get("context"), visual, "/data/context") if data.get("context") else ""
        source = heading("small", data.get("source"), visual, "/data/source", "data-source") if data.get("source") else ""
        body = f'{title}<div class="metric">{value}{label_text}</div>{context}{source}'
    elif component == "chart":
        body = f'{title}{render_chart(slide, visual)}'
    elif component == "table":
        body = f'{title}{render_table(slide, visual)}'
    else:  # pragma: no cover - registry validation prevents this.
        raise ValueError(f"unsupported component renderer: {component}")
    footer = heading("small", slide.get("footer"), visual, "/footer", "footer") if slide.get("footer") else ""
    notes = text(slide.get("notes") or "无讲者备注")
    speaker_notes = f'<aside class="speaker-notes" hidden>{notes}</aside>'
    label = slide.get("title") or slide.get("quote") or slide["id"]
    suppressions = " ".join(f"suppress-{value}" for value in visual.get("suppressions") or [])
    classes = f'slide component-{component} presentation-{presentation} treatment-{treatment} {suppressions}'.strip()
    data_attrs = f'data-component="{component}" data-presentation="{presentation}" data-language="{base_language}" data-treatment="{treatment}" data-support="{visual["carrierSupport"]}"'
    return f'<section class="{classes}" style="{style}" {data_attrs} id="{text(slide["id"])}" role="region" aria-label="{text(label)}">{body}{footer}{speaker_notes}</section>'


CSS = r"""
:root{--paper:#__PAPER__;--ink:#__INK__;--muted:#__MUTED__;--accent:#__ACCENT__;--surface:#__SURFACE__;--line:#__LINE__;--title:__TITLE_FONT__;--body:__BODY_FONT__;--meta:__META_FONT__;--radius:__RADIUS__;--density:__DENSITY__}
*{box-sizing:border-box}html{-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale}body{margin:0;background:#15171b;color:var(--ink);font-family:var(--body)}#deck{width:100%;transition:transform .5s cubic-bezier(.2,0,0,1)}.js body{overflow:hidden}.js #deck{display:flex;width:100vw;height:100vh}.js .slide{flex:0 0 100vw;height:100vh;min-height:0}.static.js body{overflow:auto}.static.js #deck{display:block;width:auto;height:auto}.static.js .slide{display:block;width:auto;height:auto;min-height:100vh}
.slide{--page:var(--slide-paper,var(--paper));--text:var(--slide-ink,var(--ink));--panel:var(--slide-surface,var(--surface));min-height:100vh;padding:7vh 9vw;background:var(--page);color:var(--text);position:relative;overflow:hidden;isolation:isolate}.slide::before{content:"";position:absolute;inset:0;z-index:-1;pointer-events:none;opacity:.52}.language-precision-modern .slide::before{background-image:linear-gradient(to right,transparent calc(100% - 1px),rgba(17,17,17,.08) 1px);background-size:8.333% 100%}.language-editorial-archive .slide::before,.language-warm-narrative .slide::before{background-image:radial-gradient(circle,rgba(70,48,32,.08) 0 1px,transparent 1.3px);background-size:24px 21px}.language-soft-product .slide::before{background:radial-gradient(circle at 88% 6%,rgba(40,132,151,.2),transparent 30%)}.language-research-organic .slide::before{background:linear-gradient(140deg,transparent 65%,rgba(57,115,91,.09))}.language-bold-statement .slide::before{background:linear-gradient(90deg,var(--accent) 0 1.5%,transparent 1.5%)}.suppress-background-grid::before{background:none!important}
h1,h2,h3{font-family:var(--title);margin:.18em 0;line-break:strict;text-wrap:balance}h1{font-size:clamp(3rem,7vw,7rem);line-height:.92;max-width:min(20ch,82vw)}h2{font-size:clamp(2rem,3.7vw,4.2rem);line-height:1.02;max-width:18ch}p,li,figcaption,blockquote{text-wrap:pretty;line-break:strict}.phrase{white-space:nowrap}.prefer-single-line{white-space:nowrap}.sub{font-size:clamp(1.2rem,2.1vw,2.2rem);max-width:36rem;line-height:1.4}.eyebrow,.data-source{color:var(--accent);font-family:var(--meta);letter-spacing:.08em}.cta{display:inline-block;margin-top:2rem;padding:.7rem 1rem;background:var(--accent);color:var(--paper);border-radius:var(--radius)}
.hero-copy{position:relative;z-index:1;display:flex;flex-direction:column;justify-content:flex-end;min-height:68vh}.items{display:grid;gap:2vw;margin-top:7vh}.items-collection{grid-template-columns:repeat(auto-fit,minmax(12rem,1fr))}.items-comparison{grid-template-columns:repeat(2,1fr)}.items-sequence{grid-template-columns:repeat(auto-fit,minmax(10rem,1fr));counter-reset:step}.item{position:relative;padding:1.5rem;border:1px solid var(--line);background:var(--panel);border-radius:var(--radius)}.item h3{color:var(--accent);font-size:clamp(1.4rem,2.5vw,2.5rem)}.item p{font-size:clamp(.95rem,1.45vw,1.35rem);line-height:1.45}.item-number{display:block;margin-bottom:2rem;color:var(--accent);font-family:var(--meta)}
.presentation-panel-led .hero-copy{max-width:78vw;min-height:72vh;padding:clamp(2rem,5vw,5rem);border:1px solid var(--line);background:var(--panel);border-radius:var(--radius);box-shadow:0 22px 64px rgba(20,35,55,.1)}.presentation-editorial-print-led .hero-copy{padding-left:3vw;border-left:3px solid var(--accent)}.presentation-editorial-print-led:not(.component-quote)>h2{padding-top:.45em;border-top:2px solid var(--text)}
.presentation-schematic-led .item,.presentation-hand-drawn-explainer .item{background:transparent;border-width:0 0 2px}.presentation-hand-drawn-explainer .item{border-style:dashed;transform:rotate(var(--tilt,0deg))}.presentation-editorial-print-led .item{border-width:1px 0 0;background:transparent}.presentation-panel-led .item,.presentation-ui-product-led .item{box-shadow:0 18px 50px rgba(20,35,55,.1)}
.relationship{display:grid;grid-template-columns:3fr 2fr;gap:4vw;margin-top:8vh}.nodes{display:grid;grid-template-columns:repeat(2,1fr);gap:1rem}.node{padding:1.3rem;border:1px solid var(--line);background:var(--panel);border-radius:var(--radius)}.node strong,.node span{display:block}.node strong{font-size:1.3rem;color:var(--accent)}.node span{margin-top:.5rem}.edges{margin:0;padding:1.2rem 1.2rem 1.2rem 2.4rem;border-left:2px solid var(--accent)}.edges li{padding:.45rem 0}.edges span{display:block;color:var(--muted)}.presentation-panel-led .node{box-shadow:0 16px 40px rgba(20,35,55,.1)}.presentation-schematic-led .node{background:transparent;border-width:0 0 2px}.presentation-hand-drawn-explainer .node{background:transparent;border-style:dashed;border-radius:42% 58% 49% 51%}.presentation-hand-drawn-explainer .node:nth-child(even){transform:rotate(1deg)}.presentation-hand-drawn-explainer .node:nth-child(odd){transform:rotate(-1deg)}.presentation-hand-drawn-explainer .edges{border-left-style:dashed}
.split{display:grid;grid-template-columns:1fr 1.15fr;gap:5vw;align-items:center;min-height:72vh}.split p{font-size:clamp(1rem,1.7vw,1.55rem);line-height:1.5}.media-grid{display:grid;gap:1rem}.media-count-2{grid-template-columns:repeat(2,minmax(0,1fr))}.media-count-3{grid-template-columns:repeat(3,minmax(0,1fr))}.media-count-2 .media-item img,.media-count-3 .media-item img{max-height:38vh}.media-item{margin:0;min-width:0}.media-item img,.media-placeholder{width:100%;max-height:58vh;object-fit:contain;border-radius:var(--radius);background:var(--panel);box-shadow:0 16px 50px rgba(0,0,0,.12)}.media-placeholder{min-height:18rem;padding:3rem;display:flex;flex-direction:column;justify-content:space-between;border:1px solid var(--line)}.media-placeholder span{font-family:var(--meta);color:var(--accent)}.media-item figcaption{margin-top:.7rem;color:var(--muted)}.presentation-photo-led .split{grid-template-columns:.7fr 1.3fr}.presentation-photo-led .media-item img{max-height:68vh;object-fit:cover}.presentation-ui-product-led .media-item{padding:clamp(.35rem,1vw,1rem);background:color-mix(in srgb,var(--text) 9%,var(--panel));border:1px solid var(--line);border-radius:calc(var(--radius) + 8px);box-shadow:0 24px 70px rgba(20,35,55,.18)}.presentation-ui-product-led .media-item img{box-shadow:none}
blockquote{position:absolute;inset:0;margin:0;padding:18vh 13vw;background:var(--page);color:var(--text);font-size:4rem}blockquote strong{display:block;font:700 clamp(2.4rem,5vw,5.3rem)/1.18 var(--title)}blockquote cite{display:block;margin-top:3rem;color:var(--accent);font:normal 1rem/1.3 var(--meta)}.presentation-editorial-print-led blockquote{padding-left:16vw;box-shadow:inset .35rem 0 var(--accent)}
.metric{display:flex;align-items:end;gap:2rem;margin-top:7vh}.metric strong{font:750 clamp(7rem,20vw,18rem)/.75 var(--title);color:var(--accent);letter-spacing:-.08em}.metric span{padding-bottom:1rem;font-size:1.2rem}.component-metric>p{max-width:34rem;font-size:1.4rem;line-height:1.5}.data-source{display:block;margin-top:1.2rem;font-size:.72rem}.presentation-panel-led .metric,.presentation-panel-led .chart{padding:2rem;border:1px solid var(--line);background:var(--panel);border-radius:var(--radius);box-shadow:0 18px 50px rgba(20,35,55,.1)}.presentation-editorial-print-led .chart{padding-top:1.5rem;border-top:2px solid var(--text)}
.chart{margin-top:6vh;max-width:66rem}.chart-row{display:grid;grid-template-columns:9rem 1fr;align-items:center;gap:1.2rem;margin:1rem 0}.chart-category{font-weight:700}.bar-group{display:grid;gap:.28rem}.bar-track{height:1.35rem;background:color-mix(in srgb,var(--line) 28%,transparent);overflow:hidden;border-radius:var(--radius)}.bar{display:block;width:calc(var(--value)*100%);height:100%;min-width:2px;background:var(--accent);position:relative}.bar b{position:absolute;right:.45rem;top:50%;transform:translateY(-50%);color:var(--paper);font-variant-numeric:tabular-nums}.series-2{background:var(--ink)!important}.series-3{background:var(--muted)!important}.chart-legend{display:flex;gap:1rem;margin-top:1rem;color:var(--muted)}.chart-legend i{display:inline-block;width:.8rem;height:.8rem;margin-right:.3rem;background:var(--accent)}.chart-legend b{font-weight:inherit}.chart-line svg{width:100%;height:50vh;border-left:1px solid var(--line);border-bottom:1px solid var(--line)}.chart-line .series{stroke:var(--accent);stroke-width:1.5}.chart-line .series-2{stroke:var(--ink)}.chart-labels{display:flex;justify-content:space-between;color:var(--muted)}
.table-wrap{margin-top:5vh}.table-wrap table{width:100%;border-collapse:collapse;background:var(--panel);font-size:clamp(.78rem,1.15vw,1.05rem)}th,td{padding:.8rem 1rem;border-bottom:1px solid var(--line);text-align:left}th{color:var(--accent);font-family:var(--meta);letter-spacing:.05em}.presentation-panel-led table,.presentation-ui-product-led table{border:1px solid var(--line);border-radius:var(--radius);overflow:hidden}.presentation-editorial-print-led table{background:transparent;border-top:2px solid var(--text)}
.treatment-inverse{--page:var(--ink);--text:var(--paper);--panel:#252525}.treatment-section-emphasis{--panel:var(--accent);box-shadow:inset .38rem 0 var(--accent)}.treatment-dense{padding-top:5vh;padding-bottom:5vh}.footer{position:absolute;left:9vw;bottom:2rem;color:var(--muted);font-family:var(--meta)}
.static #deck,.instant #deck{transition:none}#audit-report{display:none}nav{position:fixed;right:1.2rem;bottom:1rem;z-index:4;padding:.25rem;border-radius:999px;background:rgba(15,17,20,.75);backdrop-filter:blur(12px)}button{min-width:40px;min-height:40px;border:0;border-radius:999px;background:transparent;color:#fff;cursor:pointer}button:focus-visible{outline:3px solid #8eb5ff;outline-offset:2px}
@media(max-width:700px){.split,.relationship{grid-template-columns:1fr}.items{grid-template-columns:1fr}.slide{padding:7vh 7vw}.hero-copy{min-height:74vh}.footer{left:7vw}.chart-row{grid-template-columns:6rem 1fr}.prefer-single-line{white-space:normal}blockquote{padding-left:7vw;padding-right:7vw}blockquote strong{font-size:clamp(1.8rem,8vw,2.4rem)}.presentation-editorial-print-led blockquote{padding-left:9vw}}
@media(prefers-reduced-motion:reduce){#deck{transition:none}}
"""

SCRIPT = r"""
addEventListener('error',()=>{document.documentElement.classList.add('static');const d=document.querySelector('#deck');if(d)d.style.transform='none';document.querySelectorAll('.slide').forEach(s=>{s.setAttribute('aria-hidden','false');s.dataset.current='static'});setTimeout(()=>{try{publishAudit()}catch{}},0)},{once:true});
const params=new URLSearchParams(location.search);if(params.has('fail-js'))throw new Error('intentional runtime failure');document.documentElement.classList.add('js');if(params.has('static')||params.has('reduced'))document.documentElement.classList.add('static');if(params.has('instant'))document.documentElement.classList.add('instant');if(params.has('fail-init'))throw new Error('intentional initialization failure');
const deck=document.querySelector('#deck'),slides=[...document.querySelectorAll('.slide')],status=document.querySelector('#status');let index=0;
function fitPhrases(){document.querySelectorAll('.prefer-single-line-intent').forEach(el=>{el.classList.add('prefer-single-line','single-line-probe');if(el.scrollWidth>el.clientWidth+1)el.classList.remove('prefer-single-line');el.classList.remove('single-line-probe')})}
function checkOverflow(){const stat=document.documentElement.classList.contains('static');return slides.every(s=>s.scrollWidth<=s.clientWidth+1&&(stat||s.scrollHeight<=s.clientHeight+1))?'pass':'fail'}
function lineCount(element){const range=document.createRange();range.selectNodeContents(element);const tops=[...range.getClientRects()].filter(rect=>rect.width>0&&rect.height>0).map(rect=>Math.round(rect.top*10)/10);return Math.max(1,new Set(tops).size)}
function auditSnapshot(){const current=slides[index];const rect=current.getBoundingClientRect();const stat=document.documentElement.classList.contains('static');const phraseOverflow=[...current.querySelectorAll('.phrase')].filter(item=>item.getBoundingClientRect().width>current.clientWidth+1).map(item=>item.textContent);const textFlows={};current.querySelectorAll('[data-text-path]').forEach(item=>textFlows[item.dataset.textPath]=lineCount(item));const transition=parseFloat(getComputedStyle(deck).transitionDuration||'0')*1000;const overflowSlides=slides.filter(slide=>slide.scrollWidth>slide.clientWidth+1||(!stat&&slide.scrollHeight>slide.clientHeight+1)).map(slide=>({id:slide.id,scrollWidth:slide.scrollWidth,clientWidth:slide.clientWidth,scrollHeight:slide.scrollHeight,clientHeight:slide.clientHeight}));return{currentId:current.id,statusText:status.textContent,transitionMs:Math.round(transition),offsetErrorPx:Math.round(Math.abs(rect.left)*100)/100,overflow:checkOverflow(),overflowSlides,phraseOverflow,textFlows,tableBackground:current.classList.contains('component-table')?getComputedStyle(current,'::before').backgroundImage:null,staticClass:stat,visible:[...slides].filter(slide=>slide.getAttribute('aria-hidden')!=='true').length,motion:matchMedia('(prefers-reduced-motion:reduce)').matches?'reduced':'full',responsive:slides.every(slide=>slide.getBoundingClientRect().width<=innerWidth+1)?'pass':'fail'}}
function publishAudit(){const output=document.querySelector('#audit-report');if(output)output.textContent=JSON.stringify(auditSnapshot())}
function go(value){index=Math.max(0,Math.min(slides.length-1,value));const stat=document.documentElement.classList.contains('static');deck.style.transform=stat?'none':`translateX(${-index*100}vw)`;status.textContent=`${index+1} / ${slides.length}`;slides.forEach((slide,current)=>{slide.setAttribute('aria-hidden',stat?'false':current===index?'false':'true');slide.dataset.current=stat?'static':current===index?'true':'false'});publishAudit()}
document.documentElement.dataset.motion=matchMedia('(prefers-reduced-motion:reduce)').matches?'reduced':'full';fitPhrases();document.documentElement.dataset.responsive=slides.every(s=>s.getBoundingClientRect().width<=innerWidth+1)?'pass':'fail';document.documentElement.dataset.overflow=checkOverflow();go(Number(params.get('slide')||0));document.fonts?.ready.then(()=>{fitPhrases();publishAudit()});if(params.has('fail-after'))setTimeout(()=>{throw new Error('intentional post-navigation failure')},0);
next.onclick=()=>go(index+1);prev.onclick=()=>go(index-1);addEventListener('keydown',event=>{if(['ArrowRight','PageDown',' '].includes(event.key))go(index+1);if(['ArrowLeft','PageUp'].includes(event.key))go(index-1)});let touchY;addEventListener('touchstart',event=>touchY=event.touches[0].clientY);addEventListener('touchend',event=>{if(touchY-event.changedTouches[0].clientY>40)go(index+1);if(event.changedTouches[0].clientY-touchY>40)go(index-1)});addEventListener('wheel',event=>{if(Math.abs(event.deltaY)>30)go(index+(event.deltaY>0?1:-1))},{passive:true});addEventListener('resize',()=>{fitPhrases();document.documentElement.dataset.overflow=checkOverflow();publishAudit()});
"""


def render_document(data: dict[str, Any], plan: dict[str, Any], input_path: Path, *, allow_candidate: bool = False) -> str:
    normalized = normalize_deck(data)
    pages = resolved_pages(plan, normalized, "html", allow_candidate=allow_candidate)
    language_id = plan["language"]["id"]
    theme = language(language_id)
    cards = "".join(render_slide(slide, visual, input_path, language_id) for slide, visual in zip(normalized["slides"], pages, strict=True))
    css = CSS.replace("__PAPER__", theme["paper"]).replace("__INK__", theme["ink"]).replace("__MUTED__", theme["muted"]).replace("__ACCENT__", theme["accent"]).replace("__SURFACE__", theme["surface"]).replace("__LINE__", theme["line"]).replace("__TITLE_FONT__", f'{theme["title_latin"]},"{theme["title_ea"]}",sans-serif').replace("__BODY_FONT__", f'{theme["body_latin"]},"{theme["body_ea"]}",sans-serif').replace("__META_FONT__", f'{theme["meta_latin"]},"{theme["meta_ea"]}",monospace').replace("__RADIUS__", theme["radius"]).replace("__DENSITY__", theme["density"])
    return f'<!doctype html><html lang="{text(normalized.get("language") or "zh-CN")}" class="language-{language_id}" data-language="{language_id}" data-preset="{text(plan.get("preset"))}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><title>{text(normalized["deck"]["title"])} · {text(theme["label"])}</title><style>{css}</style></head><body><main id="deck">{cards}</main><nav aria-label="演示导航"><button id="prev" type="button" aria-label="上一页">←</button><span id="status" aria-live="polite"></span><button id="next" type="button" aria-label="下一页">→</button></nav><pre id="audit-report" hidden></pre><script>{SCRIPT}</script></body></html>'


def publish_html(data: dict[str, Any], plan: dict[str, Any], input_path: Path, output: Path, *, allow_candidate: bool = False) -> None:
    if output.suffix.lower() != ".html":
        raise SystemExit("输出路径必须以 .html 结尾")
    output.parent.mkdir(parents=True, exist_ok=True)
    html = render_document(data, plan, input_path, allow_candidate=allow_candidate)
    with tempfile.TemporaryDirectory(prefix=f".{output.stem}-candidate-", dir=output.parent) as temporary:
        candidate = Path(temporary) / output.name
        candidate.write_text(html, encoding="utf-8")
        subprocess.run([sys.executable, str(Path(__file__).with_name("validate_html.py")), str(candidate)], check=True, text=True)
        os.replace(candidate, output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--preset", choices=PRESETS)
    parser.add_argument("--style", choices=PRESETS, help="deprecated alias for --preset")
    parser.add_argument("--candidate-only", action="store_true", help="required for content v3; browser-verified promotion is a separate step")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    errors = validate_deck(data)
    if errors:
        raise SystemExit("invalid mature slide content:\n- " + "\n- ".join(errors))
    preset_name = args.preset or args.style
    try:
        plan = load_plan(args.plan, data, preset_name)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    plan_errors = validate_plan(plan, data, "html")
    if plan_errors:
        raise SystemExit("invalid visual plan:\n- " + "\n- ".join(plan_errors))
    if data.get("version") == 3 and not args.candidate_only:
        raise SystemExit("content v3 HTML must be generated with --candidate-only and promoted after browser verification")
    publish_html(data, plan, args.input, args.output)


if __name__ == "__main__":
    main()
