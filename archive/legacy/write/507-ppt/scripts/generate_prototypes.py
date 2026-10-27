#!/usr/bin/env python3
"""Generate 2-3 representative HTML prototypes from one mature content package."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from design_system import PRESETS, normalize_deck
from generate_html import publish_html
from visual_plan import candidate_presets, content_sha256, plan_for_prototype_candidate, representative_slide_ids, resolved_pages


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--preset", action="append", choices=PRESETS)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    normalized = normalize_deck(data)
    selected_ids = representative_slide_ids(normalized)
    subset = dict(normalized)
    subset["slides"] = [slide for slide in normalized["slides"] if slide["id"] in selected_ids]
    presets = args.preset or candidate_presets(normalized)
    if not 2 <= len(presets) <= 3 or len(set(presets)) != len(presets):
        raise SystemExit("prototype generation requires 2-3 distinct presets")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    prototype_content = args.output_dir / "prototype-content.json"
    prototype_content.write_text(json.dumps(subset, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    candidates: list[dict[str, object]] = []
    for index, preset_name in enumerate(presets, start=1):
        candidate_id = chr(64 + index)
        plan = plan_for_prototype_candidate(subset, preset_name, candidate_id, selected_ids)
        html_name = f"candidate-{chr(96 + index)}-{preset_name}.html"
        plan_name = f"candidate-{chr(96 + index)}-{preset_name}.visual-plan.json"
        (args.output_dir / plan_name).write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        publish_html(subset, plan, prototype_content, args.output_dir / html_name, allow_candidate=True)
        html_support = resolved_pages(plan, subset, "html", allow_candidate=True)
        pptx_support = resolved_pages(plan, subset, "pptx", allow_candidate=True)
        candidates.append({
            "id": candidate_id,
            "preset": preset_name,
            "language": plan["language"]["id"],
            "rationale": plan["prototype"]["rationale"],
            "presentations": [item["presentation"] for item in plan["slides"]],
            "carrierSupport": {
                "html": [item["carrierSupport"] for item in html_support],
                "pptx": [item["carrierSupport"] for item in pptx_support],
            },
            "artifact": html_name,
            "artifactSha256": digest(args.output_dir / html_name),
            "visualPlan": plan_name,
            "visualPlanSha256": digest(args.output_dir / plan_name),
        })
    cards = "".join(
        f'<article><header><strong>{item["id"]} · {item["preset"]}</strong><p>{item["rationale"]}</p></header><iframe src="{item["artifact"]}" title="候选 {item["id"]}"></iframe></article>'
        for item in candidates
    )
    index_html = f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>507-ppt 视觉组合原型</title><style>*{{box-sizing:border-box}}body{{margin:0;padding:2rem;background:#0f1115;color:#f5f6f8;font-family:system-ui,sans-serif}}h1{{margin:0 0 .5rem}}p{{color:#9da5b0}}main{{display:grid;grid-template-columns:repeat({len(candidates)},minmax(18rem,1fr));gap:1rem;margin-top:1.5rem}}article{{padding:.55rem;background:#181b21;border:1px solid #30343d;border-radius:1rem}}header{{padding:.45rem .2rem .7rem}}iframe{{display:block;width:100%;aspect-ratio:16/9;border:0;border-radius:.55rem;background:white}}@media(max-width:900px){{main{{grid-template-columns:1fr}}}}</style><h1>真实内容视觉组合原型</h1><p>代表页：{", ".join(selected_ids)}。选择或混合后，应先生成合并原型再锁定整套。</p><main>{cards}</main></html>'
    (args.output_dir / "index.html").write_text(index_html, encoding="utf-8")
    manifest = {"version": 1, "inputId": normalized.get("id"), "input": "prototype-content.json", "inputSha256": content_sha256(subset), "representativeSlides": selected_ids, "candidates": candidates, "status": "awaiting-user-selection"}
    (args.output_dir / "prototype-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"prototype package generated: {args.output_dir / 'index.html'}")


if __name__ == "__main__":
    main()
