#!/usr/bin/env python3
"""Regression checks for the three-axis 507-ppt visual system."""
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from design_system import COMPONENTS, DESIGN_LANGUAGES, PRESETS, PRESENTATIONS, TREATMENTS, normalize_deck, preferred_presentation, resolve_combination, validate_deck
from generate_html import asset_uri, render_chart
from text_layout import flow_classes, html_text, pptx_text, validate_text_flow
from visual_plan import load_plan, plan_for_preset, plan_for_prototype_candidate, representative_slide_ids, text_at, validate_plan

ROOT = Path(__file__).resolve().parents[1]
SHOWCASE = ROOT / "scripts/fixtures/system-showcase.json"
SHOWCASE_PLAN = ROOT / "scripts/fixtures/system-showcase.visual-plan.json"
LEGACY = ROOT / "scripts/fixtures/collaboration-baseline.json"
PAIRWISE = ROOT / "scripts/fixtures/presentation-pairwise.json"
PAIRWISE_PLAN = ROOT / "scripts/fixtures/presentation-pairwise.visual-plan.json"


class DesignSystemTests(unittest.TestCase):
    def setUp(self) -> None:
        self.showcase = json.loads(SHOWCASE.read_text(encoding="utf-8"))
        self.plan = json.loads(SHOWCASE_PLAN.read_text(encoding="utf-8"))

    def test_showcase_covers_every_semantic_leaf_component(self) -> None:
        self.assertEqual(validate_deck(self.showcase), [])
        normalized = normalize_deck(self.showcase)
        self.assertEqual({slide["component"] for slide in normalized["slides"]}, set(COMPONENTS))

    def test_languages_have_complete_distinct_tokens(self) -> None:
        required = {"paper", "ink", "muted", "accent", "surface", "line", "title_ea", "title_latin", "body_ea", "body_latin", "meta_latin", "radius", "density", "grid", "surface_depth"}
        signatures = set()
        for name, item in DESIGN_LANGUAGES.items():
            self.assertTrue(required.issubset(item), name)
            signatures.add((item["paper"], item["accent"], item["title_latin"], item["radius"], item["grid"]))
        self.assertEqual(len(signatures), len(DESIGN_LANGUAGES))

    def test_presets_map_to_languages(self) -> None:
        self.assertEqual(set(PRESETS), {"swiss", "magazine", "cobalt", "clay", "forest", "noir"})
        self.assertTrue(all(item["language"] in DESIGN_LANGUAGES for item in PRESETS.values()))

    def test_every_component_and_presentation_has_a_live_consumer(self) -> None:
        preferred = {preferred_presentation(name) for name in COMPONENTS}
        self.assertTrue(preferred.issubset(PRESENTATIONS))
        used = {presentation for component in COMPONENTS.values() for presentation in component["presentations"]}
        self.assertEqual(used, set(PRESENTATIONS))
        for item in PRESENTATIONS.values():
            self.assertIn(item["carriers"]["html"], {"native", "adapted"})
            self.assertIn(item["carriers"]["pptx"], {"native", "adapted"})

    def test_public_component_presentation_matrix_does_not_drift(self) -> None:
        expected = {
            "cover": {"type-led", "panel-led", "editorial-print-led"},
            "section": {"type-led", "panel-led", "editorial-print-led"},
            "closing": {"type-led", "panel-led", "editorial-print-led"},
            "statement": {"type-led", "panel-led", "editorial-print-led"},
            "collection": {"panel-led", "schematic-led", "editorial-print-led", "hand-drawn-explainer"},
            "comparison": {"panel-led", "schematic-led", "editorial-print-led", "hand-drawn-explainer"},
            "sequence": {"panel-led", "schematic-led", "editorial-print-led", "hand-drawn-explainer"},
            "relationship": {"panel-led", "schematic-led", "hand-drawn-explainer"},
            "media-evidence": {"photo-led", "ui-product-led"},
            "quote": {"type-led", "editorial-print-led"},
            "metric": {"data-led", "panel-led"},
            "chart": {"data-led", "panel-led", "editorial-print-led"},
            "table": {"data-led", "panel-led", "editorial-print-led"},
        }
        self.assertEqual({name: set(item["presentations"]) for name, item in COMPONENTS.items()}, expected)

    def test_registered_combination_matrix_resolves_for_both_carriers(self) -> None:
        slides = {slide["component"]: slide for slide in normalize_deck(self.showcase)["slides"]}
        resolved = 0
        for component, contract in COMPONENTS.items():
            for presentation in contract["presentations"]:
                slide = deepcopy(slides[component])
                slide["assets"] = [{"id": "matrix", "role": "ui", "alt": "matrix fixture"}]
                for language_id in DESIGN_LANGUAGES:
                    for carrier in ("html", "pptx"):
                        result = resolve_combination(component, presentation, language_id, carrier, slide)
                        self.assertIn(result["carrierSupport"], {"native", "adapted"})
                        resolved += 1
        self.assertEqual(resolved, sum(len(item["presentations"]) for item in COMPONENTS.values()) * len(DESIGN_LANGUAGES) * 2)

    def test_pairwise_fixture_covers_presentations_and_treatments(self) -> None:
        content = json.loads(PAIRWISE.read_text(encoding="utf-8"))
        plan = json.loads(PAIRWISE_PLAN.read_text(encoding="utf-8"))
        self.assertEqual(validate_deck(content), [])
        self.assertEqual(validate_plan(plan, content), [])
        self.assertEqual({item["presentation"] for item in plan["slides"]}, set(PRESENTATIONS))
        self.assertEqual({item["treatment"] for item in plan["slides"]}, set(TREATMENTS))

    def test_table_suppresses_competing_grid_rules(self) -> None:
        resolved = resolve_combination("table", "data-led", "precision-modern", "html")
        self.assertIn("background-grid", resolved["suppressions"])
        self.assertIn("decorative-rules", resolved["suppressions"])

    def test_photo_presentation_is_not_accepted_when_renderer_does_not_consume_assets(self) -> None:
        slide = {"assets": [{"id": "hero", "role": "photo", "path": "hero.png", "alt": "hero"}]}
        with self.assertRaisesRegex(ValueError, "incompatible"):
            resolve_combination("cover", "photo-led", "precision-modern", "html", slide)

    def test_data_evidence_subtypes_are_not_interchangeable(self) -> None:
        broken = json.loads(json.dumps(self.showcase))
        chart = next(slide for slide in broken["slides"] if slide["id"] == "chart")
        chart["data"].pop("series")
        self.assertTrue(any("chart requires 1-3 series" in item for item in validate_deck(broken)))
        table = next(slide for slide in broken["slides"] if slide["id"] == "table")
        table["data"]["rows"][0] = ["too", "short"]
        self.assertTrue(any("table rows must match columns" in item for item in validate_deck(broken)))

    def test_media_evidence_requires_explicit_asset_paths(self) -> None:
        broken = deepcopy(self.showcase)
        media = next(slide for slide in broken["slides"] if slide["id"] == "media")
        media["assets"][0].pop("path")
        self.assertTrue(any("assets require path" in item for item in validate_deck(broken)))

    def test_missing_html_asset_never_becomes_a_semantic_placeholder(self) -> None:
        with self.assertRaisesRegex(FileNotFoundError, "missing-client-shot"):
            asset_uri({"id": "client", "path": "missing-client-shot.png", "alt": "client"}, SHOWCASE)

    def test_multi_series_html_chart_uses_independent_tracks(self) -> None:
        slide = {
            "title": "双序列",
            "data": {
                "chartType": "bar",
                "categories": ["A", "B"],
                "series": [{"name": "基线", "values": [2, 4]}, {"name": "当前", "values": [3, 5]}],
                "scale": {"min": 0, "max": 5},
            },
        }
        html = render_chart(slide, {"textFlow": {}})
        self.assertEqual(html.count('class="bar-track"'), 4)

    def test_three_series_bar_chart_preserves_zero_and_maximum_boundaries(self) -> None:
        slide = {
            "title": "三序列",
            "data": {
                "chartType": "bar",
                "categories": ["A", "B"],
                "series": [
                    {"name": "一", "values": [0, 6]},
                    {"name": "二", "values": [2, 4]},
                    {"name": "三", "values": [3, 5]},
                ],
                "scale": {"min": 0, "max": 6},
            },
        }
        html = render_chart(slide, {"textFlow": {}})
        self.assertEqual(html.count('class="bar-track"'), 6)
        self.assertIn("--value:0.000000", html)
        self.assertIn("--value:1.000000", html)
        self.assertIn("series-3", html)

    def test_line_chart_renders_every_series_and_category(self) -> None:
        slide = {
            "title": "趋势",
            "data": {
                "chartType": "line",
                "categories": ["一月", "二月", "三月"],
                "series": [{"name": "基线", "values": [1, 2, 3]}, {"name": "当前", "values": [2, 4, 5]}],
            },
        }
        html = render_chart(slide, {"textFlow": {}})
        self.assertEqual(html.count("<polyline"), 2)
        for value in ("一月", "二月", "三月", "基线", "当前"):
            self.assertIn(value, html)

    def test_legacy_fixture_normalizes_without_changing_identity(self) -> None:
        raw = json.loads(LEGACY.read_text(encoding="utf-8"))
        normalized = normalize_deck(raw)
        self.assertEqual([slide["id"] for slide in raw["slides"]], [slide["id"] for slide in normalized["slides"]])
        self.assertEqual([slide["component"] for slide in normalized["slides"]], ["cover", "media-evidence", "collection", "quote"])
        self.assertEqual(normalized["slides"][1]["assets"][0]["caption"], raw["slides"][1]["caption"])
        self.assertEqual(validate_deck(raw), [])

    def test_visual_plan_and_phrase_flow_are_valid(self) -> None:
        self.assertEqual(validate_plan(self.plan, self.showcase), [])
        flow = next(item for item in self.plan["slides"] if item["id"] == "chart")["textFlow"]["/title"]
        self.assertEqual(validate_text_flow("六种语言，八类呈现", flow), [])
        self.assertIn("<wbr>", html_text("六种语言，八类呈现", flow))
        self.assertIn("prefer-single-line-intent", flow_classes(flow))
        self.assertEqual(pptx_text("六种语言，八类呈现", flow), "六种语言，\v八类呈现")

    def test_nested_text_flow_paths_validate(self) -> None:
        plan = deepcopy(self.plan)
        table = next(item for item in plan["slides"] if item["id"] == "table")
        table["textFlow"]["/data/rows/0/2"] = {"units": ["网格与层级"], "lines": ["网格与层级"], "preferSingleLine": True, "maxLines": 1}
        self.assertEqual(validate_plan(plan, self.showcase), [])
        table_slide = next(slide for slide in normalize_deck(self.showcase)["slides"] if slide["id"] == "table")
        self.assertEqual(text_at(table_slide, "/data/rows/0/2"), "网格与层级")
        self.assertIsNone(text_at(table_slide, "/notes"))

    def test_visual_plan_rejects_raw_token_overrides(self) -> None:
        plan = deepcopy(self.plan)
        plan["slides"][0]["tokens"] = {"accent": "FF00FF"}
        self.assertTrue(any("unsupported visual-plan field" in error for error in validate_plan(plan, self.showcase)))

    def test_invalid_phrase_split_is_rejected(self) -> None:
        errors = validate_text_flow("人工智能", {"units": ["人工", "智能"], "lines": ["人工智", "能"]})
        self.assertIn("text flow lines may break only between units", errors)

    def test_one_character_tail_line_is_rejected(self) -> None:
        errors = validate_text_flow("人工智能化", {"units": ["人工智能", "化"], "lines": ["人工智能", "化"]})
        self.assertIn("text flow cannot leave a one-or-two-character tail line", errors)

    def test_explicit_lines_cannot_exceed_max_lines(self) -> None:
        errors = validate_text_flow("人工智能治理风险边界", {"units": ["人工", "智能治理", "风险边界"], "lines": ["人工", "智能治理", "风险边界"], "maxLines": 2})
        self.assertIn("text flow lines exceed maxLines", errors)

    def test_legacy_preset_builds_a_valid_plan(self) -> None:
        legacy = json.loads(LEGACY.read_text(encoding="utf-8"))
        for name in PRESETS:
            self.assertEqual(validate_plan(plan_for_preset(legacy, name), legacy), [], name)

    def test_v3_requires_plan_or_explicit_preset_while_legacy_keeps_default(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires --plan"):
            load_plan(None, self.showcase)
        self.assertEqual(load_plan(None, self.showcase, "swiss")["prototype"]["status"], "skipped")
        legacy = json.loads(LEGACY.read_text(encoding="utf-8"))
        self.assertEqual(load_plan(None, legacy)["preset"], "swiss")

    def test_candidate_plan_is_only_valid_for_prototype_rendering(self) -> None:
        plan = plan_for_preset(self.showcase, "swiss", prototype_status="candidate")
        self.assertTrue(any("prototype status" in error for error in validate_plan(plan, self.showcase, "html")))
        self.assertEqual(validate_plan(plan, self.showcase, "html", allow_candidate=True), [])

    def test_approved_plan_requires_a_bound_prototype_manifest(self) -> None:
        plan = plan_for_preset(self.showcase, "swiss", prototype_status="approved")
        self.assertTrue(any("approved prototype" in error for error in validate_plan(plan, self.showcase)))

    def test_mixed_plan_rejects_unbound_merged_prototype(self) -> None:
        plan = deepcopy(self.plan)
        plan["prototype"]["mixedFrom"] = ["A", "B"]
        plan["prototype"]["mergedPrototype"] = {
            "artifact": "does-not-exist.html",
            "artifactSha256": "0" * 64,
            "visualPlan": "does-not-exist.visual-plan.json",
            "visualPlanSha256": "0" * 64,
            "evidence": "does-not-exist.png",
            "evidenceSha256": "0" * 64,
        }
        errors = validate_plan(plan, self.showcase)
        self.assertTrue(any("merged prototype" in error and "missing" in error for error in errors), errors)

    def test_prototype_candidates_change_language_and_page_treatment(self) -> None:
        normalized = normalize_deck(self.showcase)
        selected = representative_slide_ids(normalized)
        subset = dict(normalized)
        subset["slides"] = [slide for slide in normalized["slides"] if slide["id"] in selected]
        plans = [plan_for_prototype_candidate(subset, name, candidate, selected) for name, candidate in (("swiss", "A"), ("cobalt", "B"), ("magazine", "C"))]
        self.assertEqual(len({plan["language"]["id"] for plan in plans}), 3)
        self.assertGreater(len({tuple(item["presentation"] for item in plan["slides"]) for plan in plans}), 1)
        for plan in plans:
            self.assertEqual(validate_plan(plan, subset, "html", allow_candidate=True), [])

    def test_html_renders_every_component_from_one_plan(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "showcase.html"
            subprocess.run(["python3", "-B", str(ROOT / "scripts/generate_html.py"), "--input", str(SHOWCASE), "--plan", str(SHOWCASE_PLAN), "--candidate-only", "--output", str(output)], check=True)
            html = output.read_text(encoding="utf-8")
            self.assertIn('data-language="precision-modern"', html)
            for component in COMPONENTS:
                self.assertIn(f'data-component="{component}"', html)
            self.assertIn("suppress-background-grid", html)
            self.assertIn('data-text-path="/data/rows/0/2"', html)
            self.assertIn('<span class="phrase">网格与层级</span>', html)


if __name__ == "__main__":
    unittest.main()
