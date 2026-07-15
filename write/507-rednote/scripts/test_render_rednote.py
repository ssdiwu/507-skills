import copy
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import render_rednote as renderer
import render_style_gallery as gallery


class RenderRednoteTests(unittest.TestCase):
    def setUp(self):
        self.spec_path = SCRIPT_DIR / "fixtures" / "sample-project.json"
        self.spec = json.loads(self.spec_path.read_text(encoding="utf-8"))

    def test_fixture_is_valid_and_renders_self_contained_html(self):
        renderer.validate_spec(self.spec)
        output = renderer.render_html(self.spec, self.spec_path)
        self.assertIn("data:image/svg+xml;base64,", output)
        self.assertNotIn("sample.svg", output)
        self.assertIn('class="page cover" data-page="1"', output)
        self.assertIn('data-source-map="M1 / 标题与中心判断"', output)
        self.assertIn('data-source-map="M2 / 论证链第 1 步"', output)
        self.assertIn('<body class="theme-newspaper layout-longform">', output)
        self.assertIn('id="flow-source"', output)
        self.assertIn('id="flow-page-template"', output)
        self.assertIn('class="flow-unit" data-heading="" data-source-map="M3 / 论证链第 2 步（续页）"', output)

    def test_cards_mode_keeps_explicit_physical_pages(self):
        spec = copy.deepcopy(self.spec)
        spec["layoutMode"] = "cards"
        output = renderer.render_html(spec, self.spec_path)
        self.assertEqual(output.count('<section class="page'), 5)
        self.assertIn('<body class="theme-newspaper layout-cards">', output)
        self.assertIn('<section class="page article continuation" data-page="3"', output)

    def test_longform_groups_the_closing_and_rebalances_the_previous_page(self):
        output = renderer.render_html(self.spec, self.spec_path)
        self.assertIn('class="flow-unit closing-group', output)
        self.assertIn("function fillRatioOf(page)", output)
        self.assertIn("closingPage.querySelector('.closing-group')", output)

    def test_rich_text_escapes_html_before_applying_markers(self):
        output = renderer.rich_text('<script>alert(1)</script> **加粗** ==强调== `code`')
        self.assertNotIn("<script>", output)
        self.assertIn("&lt;script&gt;", output)
        self.assertIn("<strong>加粗</strong>", output)
        self.assertIn('<span class="accent">强调</span>', output)
        self.assertIn("<code>code</code>", output)

    def test_rejects_remote_images(self):
        spec = copy.deepcopy(self.spec)
        spec["pages"][0]["image"] = "https://example.com/private.png"
        renderer.validate_spec(spec)
        with self.assertRaises(SystemExit):
            renderer.render_html(spec, self.spec_path)

    def test_requires_a_single_cover_at_the_front(self):
        spec = copy.deepcopy(self.spec)
        spec["pages"][0]["type"] = "article"
        spec["pages"][0]["heading"] = "错误封面"
        spec["pages"][0]["blocks"] = [{"type": "paragraph", "text": "x"}]
        with self.assertRaises(SystemExit):
            renderer.validate_spec(spec)

    def test_all_style_presets_render_and_invalid_style_fails(self):
        for style in renderer.STYLE_PRESETS:
            spec = copy.deepcopy(self.spec)
            spec["stylePreset"] = style
            renderer.validate_spec(spec)
            output = renderer.render_html(spec, self.spec_path)
            self.assertIn(f'<body class="theme-{style} layout-longform">', output)
        spec = copy.deepcopy(self.spec)
        spec["stylePreset"] = "unknown-style"
        with self.assertRaises(SystemExit):
            renderer.validate_spec(spec)
        spec = copy.deepcopy(self.spec)
        spec["layoutMode"] = "unknown-layout"
        with self.assertRaises(SystemExit):
            renderer.validate_spec(spec)

    def test_style_gallery_selection_defaults_to_all_and_rejects_unknown(self):
        self.assertEqual(gallery.parse_styles(None), list(renderer.STYLE_PRESETS))
        self.assertEqual(gallery.parse_styles("mono,newspaper,mono"), ["mono", "newspaper"])
        with self.assertRaises(SystemExit):
            gallery.parse_styles("not-a-style")

    def test_heading_is_optional_but_cannot_be_empty_when_present(self):
        spec = copy.deepcopy(self.spec)
        renderer.validate_spec(spec)
        spec["pages"][2]["heading"] = "   "
        with self.assertRaises(SystemExit):
            renderer.validate_spec(spec)

    def test_requires_source_mapping_for_every_page(self):
        for page_index in (0, 1):
            with self.subTest(page_index=page_index):
                spec = copy.deepcopy(self.spec)
                del spec["pages"][page_index]["sourceMap"]
                with self.assertRaises(SystemExit):
                    renderer.validate_spec(spec)

    def test_rejects_unknown_fields_instead_of_ignoring_typos(self):
        spec = copy.deepcopy(self.spec)
        spec["pages"][1]["sorceMap"] = "typo"
        with self.assertRaises(SystemExit):
            renderer.validate_spec(spec)

    def test_parse_pages_deduplicates_and_sorts(self):
        self.assertEqual(renderer.parse_pages("5,2,2", 5), [2, 5])
        with self.assertRaises(SystemExit):
            renderer.parse_pages("0,2", 5)

    def test_manifest_records_render_freshness_and_source_mapping(self):
        with TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            spec_path = output_dir / "rednote-project.json"
            spec_path.write_text(json.dumps(self.spec, ensure_ascii=False), encoding="utf-8")
            (output_dir / "rednote.html").write_text("<html></html>", encoding="utf-8")
            pages_dir = output_dir / "pages"
            pages_dir.mkdir()
            page_file = pages_dir / "rednote_page_01.jpg"
            page_file.write_bytes(b"jpeg-placeholder")
            page_map = [{"page": 1, "type": "cover", "sourceMap": "M1 / 标题与中心判断"}]

            renderer.write_manifest(output_dir, spec_path, self.spec, [page_file], [1], page_map)

            manifest = json.loads((output_dir / "render-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["status"], "rendered")
            self.assertEqual(manifest["sourceSpecSha256"], renderer.sha256(spec_path))
            self.assertEqual(manifest["pageMap"], page_map)


if __name__ == "__main__":
    unittest.main()
