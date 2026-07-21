import copy
import json
import shutil
import subprocess
import sys
import unittest
from argparse import Namespace
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

    def test_fixture_is_valid_and_renders_self_contained_multi_canvas_html(self):
        renderer.validate_spec(self.spec)
        output = renderer.render_html(self.spec, self.spec_path)
        self.assertIn("data:image/svg+xml;base64,", output)
        self.assertNotIn("sample.svg", output)
        self.assertIn('class="visual-editorial theme-editorial-paper"', output)
        self.assertIn('data-target="rednote-01"', output)
        self.assertIn('data-point="每页只能有一个主观点"', output)
        self.assertIn('data-layout="statement"', output)
        self.assertIn('data-target="wechat-main"', output)
        self.assertIn('data-target="wechat-share"', output)
        self.assertNotIn("layout-longform", output)

    def test_rejects_legacy_layout_and_style_fields_with_migration_message(self):
        for field in ("layoutMode", "stylePreset"):
            with self.subTest(field=field):
                spec = copy.deepcopy(self.spec)
                spec[field] = "legacy"
                with self.assertRaisesRegex(SystemExit, "旧字段"):
                    renderer.validate_spec(spec)

    def test_visual_system_and_theme_must_match(self):
        spec = copy.deepcopy(self.spec)
        spec["visualSystem"] = "swiss"
        with self.assertRaisesRegex(SystemExit, "不属于"):
            renderer.validate_spec(spec)
        spec["themePreset"] = "swiss-blue"
        renderer.validate_spec(spec)
        output = renderer.render_html(spec, self.spec_path)
        self.assertIn("visual-swiss theme-swiss-blue", output)

    def test_every_page_requires_point_source_map_and_layout(self):
        for page_index, field in ((0, "point"), (1, "sourceMap"), (2, "layout")):
            with self.subTest(page_index=page_index, field=field):
                spec = copy.deepcopy(self.spec)
                del spec["pages"][page_index][field]
                with self.assertRaises(SystemExit):
                    renderer.validate_spec(spec)

    def test_excluded_content_is_required_and_destination_is_closed(self):
        spec = copy.deepcopy(self.spec)
        del spec["excludedContent"]
        with self.assertRaisesRegex(SystemExit, "excludedContent"):
            renderer.validate_spec(spec)
        spec = copy.deepcopy(self.spec)
        spec["excludedContent"][0]["destination"] = "somewhere"
        with self.assertRaisesRegex(SystemExit, "destination"):
            renderer.validate_spec(spec)
        spec["excludedContent"] = []
        renderer.validate_spec(spec)

    def test_screenshot_has_separate_chrome_contract_and_remote_assets_fail_at_render(self):
        spec = copy.deepcopy(self.spec)
        screenshot = next(block for block in spec["pages"][2]["blocks"] if block["type"] == "screenshot")
        screenshot["chrome"] = "tablet"
        with self.assertRaisesRegex(SystemExit, "chrome"):
            renderer.validate_spec(spec)
        screenshot["chrome"] = "browser"
        screenshot["src"] = "https://example.com/private.png"
        renderer.validate_spec(spec)
        with self.assertRaisesRegex(SystemExit, "本地文件路径"):
            renderer.render_html(spec, self.spec_path)

    def test_motion_contract_limits_duration_and_requires_prepared_poster(self):
        spec = copy.deepcopy(self.spec)
        motion = {
            "type": "motion", "src": "clip.mp4", "durationSec": 3,
            "startSec": 0, "posterTimeSec": 1, "height": 320,
            "fit": "cover", "position": "center"
        }
        spec["pages"][1]["blocks"] = [motion]
        renderer.validate_spec(spec)
        with self.assertRaisesRegex(SystemExit, "首帧准备"):
            renderer.render_html(spec, self.spec_path)
        motion["durationSec"] = 6
        with self.assertRaisesRegex(SystemExit, "1–5"):
            renderer.validate_spec(spec)

    def test_rejects_more_than_one_motion_slot_per_page(self):
        spec = copy.deepcopy(self.spec)
        motion = {"type": "motion", "src": "clip.mp4", "durationSec": 2}
        spec["pages"][1]["blocks"] = [copy.deepcopy(motion), copy.deepcopy(motion)]
        with self.assertRaisesRegex(SystemExit, "最多一个"):
            renderer.validate_spec(spec)

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "requires ffmpeg/ffprobe")
    def test_motion_preparation_probes_video_and_extracts_poster(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            video = root / "clip.mp4"
            subprocess.run([
                shutil.which("ffmpeg"), "-y", "-f", "lavfi", "-i", "color=c=blue:s=320x240:d=3",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", str(video)
            ], check=True, capture_output=True)
            spec = copy.deepcopy(self.spec)
            sample = str((SCRIPT_DIR / "fixtures" / "sample.svg").resolve())
            spec["avatar"] = sample
            spec["pages"][0]["image"] = sample
            spec["pages"][2]["blocks"][0]["src"] = sample
            spec["wechatCovers"]["main"]["image"] = sample
            spec["pages"][1]["blocks"] = [{
                "type": "motion", "src": str(video), "durationSec": 2,
                "startSec": 0, "posterTimeSec": 0.5, "height": 320,
                "fit": "cover", "position": "center"
            }]
            renderer.validate_spec(spec)
            spec_path = root / "project.json"
            spec_path.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
            prepared, motions = renderer.prepare_motion_posters(spec, spec_path, root)
            block = prepared["pages"][1]["blocks"][0]
            self.assertTrue(Path(block["_poster"]).is_file())
            self.assertEqual(motions[0]["durationSec"], 2)
            output = renderer.render_html(prepared, spec_path)
            self.assertIn("data-motion-id=", output)

    def test_wechat_cover_pair_is_atomic(self):
        spec = copy.deepcopy(self.spec)
        del spec["wechatCovers"]["share"]
        with self.assertRaisesRegex(SystemExit, "同时提供"):
            renderer.validate_spec(spec)

    def test_gallery_defaults_to_all_system_theme_variants(self):
        self.assertEqual(gallery.parse_themes(None), list(renderer.THEME_PRESETS))
        self.assertEqual(gallery.parse_themes("swiss-blue,editorial-paper,swiss-blue"), ["swiss-blue", "editorial-paper"])
        with self.assertRaises(SystemExit):
            gallery.parse_themes("unknown")

    def test_section_audit_reports_layout_failures_and_motion_geometry(self):
        parser = renderer.SectionAuditParser()
        parser.feed(
            '<section data-target="rednote-02" data-page="2" data-type="article" data-point="P" '
            'data-source-map="S" data-layout="statement" data-fill-ratio="0.7" data-min-font="14" '
            'data-title-gap="8" data-overflow="true">'
            '<div data-motion-id="motion-02-01" data-motion-page="2" data-motion-x="10" data-motion-y="20" '
            'data-motion-width="300" data-motion-height="200"></div></section>'
        )
        self.assertEqual(len(parser.failures()), 3)
        self.assertEqual(parser.motions[0]["width"], 300)

    def test_manifest_records_new_contract_and_artifacts(self):
        with TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            spec_path = output_dir / "rednote-project.json"
            spec_path.write_text(json.dumps(self.spec, ensure_ascii=False), encoding="utf-8")
            html_path = output_dir / "rednote.html"
            html_path.write_text("<html></html>", encoding="utf-8")
            page = output_dir / "page.jpg"
            page.write_bytes(b"jpeg-placeholder")
            artifacts = [renderer.artifact("rednote-page", page, output_dir, (1500, 2000))]
            renderer.write_manifest(output_dir, spec_path, self.spec, artifacts, [1], [], {"chrome": "test"}, [])
            manifest = json.loads((output_dir / "render-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["visualSystem"], "editorial")
            self.assertEqual(manifest["themePreset"], "editorial-paper")
            self.assertEqual(manifest["pageMap"][1]["point"], "每页只能有一个主观点")
            self.assertEqual(manifest["excludedContent"], self.spec["excludedContent"])
            self.assertEqual(manifest["artifacts"][0]["dimensions"], [1500, 2000])

    def test_partial_render_rejects_changed_unselected_page(self):
        with TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            previous = {
                "globalSpecSha256": renderer.global_spec_hash(self.spec),
                "sourceAssetsSha256": renderer.hash_json([]),
                "pageCount": len(self.spec["pages"]),
                "pageMap": renderer.page_map_from_spec(self.spec),
            }
            (output_dir / "render-manifest.json").write_text(json.dumps(previous), encoding="utf-8")
            changed = copy.deepcopy(self.spec)
            changed["pages"][2]["point"] = "另一个观点"
            with self.assertRaisesRegex(SystemExit, "第 3 页"):
                renderer.validate_partial_render(changed, output_dir, [2], [])

    def test_wechat_pair_preview_has_stable_dimensions(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            main = root / "main.jpg"
            share = root / "share.jpg"
            Image = __import__("PIL.Image", fromlist=["Image"])
            Image.new("RGB", (2100, 900), "white").save(main)
            Image.new("RGB", (1080, 1080), "black").save(share)
            output = root / "pair.jpg"
            size = renderer.build_wechat_preview(main, share, output)
            self.assertEqual(size, (2400, 1200))
            self.assertTrue(output.is_file())

    def test_crop_position_maps_to_ffmpeg_expressions(self):
        self.assertEqual(renderer.crop_expressions("left top"), ("0", "0"))
        self.assertEqual(renderer.crop_expressions("right bottom"), ("iw-ow", "ih-oh"))
        self.assertEqual(renderer.crop_expressions("center"), ("(iw-ow)/2", "(ih-oh)/2"))


if __name__ == "__main__":
    unittest.main()
