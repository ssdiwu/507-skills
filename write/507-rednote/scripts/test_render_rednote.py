import copy
import json
import shutil
import subprocess
import sys
import unittest
from argparse import Namespace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import render_rednote as renderer
import render_style_gallery as gallery


class RenderRednoteTests(unittest.TestCase):
    def setUp(self):
        self.spec_path = SCRIPT_DIR / "fixtures" / "sample-project.json"
        self.spec = json.loads(self.spec_path.read_text(encoding="utf-8"))
        self.article_spec_path = SCRIPT_DIR / "fixtures" / "sample-article-project.json"
        self.article_spec = json.loads(self.article_spec_path.read_text(encoding="utf-8"))

    def test_fixture_is_valid_and_renders_self_contained_multi_canvas_html(self):
        renderer.validate_spec(self.spec)
        output = renderer.render_html(self.spec, self.spec_path)
        self.assertIn("data:image/svg+xml;base64,", output)
        self.assertNotIn("sample.svg", output)
        self.assertIn('class="mode-summary visual-editorial theme-editorial-paper"', output)
        self.assertIn('data-target="rednote-01"', output)
        self.assertIn('data-point="每页只能有一个主观点"', output)
        self.assertIn('data-layout="statement"', output)
        self.assertIn('data-target="wechat-main"', output)
        self.assertIn('data-target="wechat-share"', output)
        self.assertNotIn("layout-longform", output)

    def test_article_mode_renders_plain_reading_pages_without_card_chrome(self):
        renderer.validate_spec(self.article_spec)
        output = renderer.render_html(self.article_spec, self.article_spec_path)
        self.assertIn('class="mode-article visual-swiss theme-swiss-blue"', output)
        self.assertIn('class="canvas rednote-article page article article-flow"', output)
        self.assertIn('class="article-heading"', output)
        self.assertIn('class="article-list"', output)
        self.assertIn('.mode-article .article-flow .blocks > :last-child { margin-bottom:0; }', output)
        article = output.split('data-target="rednote-02"', 1)[1].split('</section>', 1)[0]
        self.assertNotIn('class="topbar"', article)
        self.assertNotIn('class="avatar"', article)
        self.assertNotIn('class="pageno"', article)
        self.assertEqual(renderer.page_canvas(self.article_spec, 1)["output"], (1500, 2000))
        self.assertEqual(renderer.page_canvas(self.article_spec, 2)["output"], (1440, 2400))

    def test_article_page_tail_uses_canvas_padding_without_double_counting_last_block_margin(self):
        output = renderer.render_html(self.article_spec, self.article_spec_path)
        self.assertIn('.mode-article .article-flow { padding:58px 56px 70px;', output)
        self.assertIn('.mode-article .article-flow .blocks > :last-child { margin-bottom:0; }', output)

    def test_article_mode_rejects_summary_page_contract_and_exclusions(self):
        spec = copy.deepcopy(self.article_spec)
        spec["pages"][1]["point"] = "不应该存在的逐页观点"
        with self.assertRaisesRegex(SystemExit, "未知字段"):
            renderer.validate_spec(spec)
        spec = copy.deepcopy(self.article_spec)
        spec["excludedContent"] = [{"summary": "删掉一段", "destination": "notUsed"}]
        with self.assertRaisesRegex(SystemExit, "必须为空"):
            renderer.validate_spec(spec)

    def test_mode_is_explicit(self):
        spec = copy.deepcopy(self.spec)
        del spec["mode"]
        with self.assertRaisesRegex(SystemExit, "mode"):
            renderer.validate_spec(spec)

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
            self.assertEqual(manifest["sourceSpec"], "rednote-project.json")
            self.assertEqual(manifest["mode"], "summary")
            self.assertEqual(manifest["visualSystem"], "editorial")
            self.assertEqual(manifest["themePreset"], "editorial-paper")
            self.assertEqual(manifest["pageMap"][1]["point"], "每页只能有一个主观点")
            self.assertEqual(manifest["excludedContent"], self.spec["excludedContent"])
            self.assertEqual(manifest["artifacts"][0]["dimensions"], [1500, 2000])

    def test_source_references_do_not_persist_machine_absolute_paths(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_dir = root / "project"
            spec_dir.mkdir()
            bundled = spec_dir / "assets" / "clip.mp4"
            bundled.parent.mkdir()
            bundled.write_bytes(b"bundled")
            external = root / "external" / "clip.mp4"
            external.parent.mkdir()
            external.write_bytes(b"external")

            self.assertEqual(
                renderer.portable_source_reference(bundled, spec_dir),
                "assets/clip.mp4",
            )
            self.assertEqual(
                renderer.portable_source_reference(external, spec_dir),
                "external-file:clip.mp4",
            )
            self.assertEqual(
                renderer.portable_source_reference("assets/clip.mp4", spec_dir),
                "assets/clip.mp4",
            )

    def test_candidate_validation_rejects_absolute_source_reference(self):
        with TemporaryDirectory() as tmp:
            candidate_dir = Path(tmp)
            manifest = {
                "sourceSpec": str(self.article_spec_path.resolve()),
                "sourceAssets": [],
                "motion": [],
            }
            (candidate_dir / "render-manifest.json").write_text(
                json.dumps(manifest),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(SystemExit, "本机绝对来源路径"):
                renderer.validate_candidate_bundle(
                    candidate_dir,
                    self.article_spec_path,
                    self.article_spec,
                    list(range(1, len(self.article_spec["pages"]) + 1)),
                )

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

    def test_full_render_failure_preserves_previous_bundle(self):
        with TemporaryDirectory(prefix="rednote-atomic-") as tmp:
            output_dir = Path(tmp) / "output"
            pages_dir = output_dir / "pages"
            pages_dir.mkdir(parents=True)
            (output_dir / "rednote.html").write_bytes(b"old-html")
            (output_dir / "contact-sheet.jpg").write_bytes(b"old-contact")
            (output_dir / "render-manifest.json").write_bytes(b"old-manifest")
            (pages_dir / "rednote_page_01.jpg").write_bytes(b"old-page")

            args = Namespace(
                spec=str(self.article_spec_path), output_dir=str(output_dir), pages=None,
                chrome=None, ffmpeg=None, ffprobe=None, makelive=None, timeout=1,
            )
            before = {
                path.relative_to(output_dir): path.read_bytes()
                for path in output_dir.rglob("*") if path.is_file()
            }
            with (
                patch.object(renderer, "find_chrome", return_value="chrome"),
                patch.object(renderer, "inspect_layout", side_effect=RuntimeError("synthetic render failure")),
            ):
                with self.assertRaisesRegex(RuntimeError, "synthetic render failure"):
                    renderer.run(args)

            after = {
                path.relative_to(output_dir): path.read_bytes()
                for path in output_dir.rglob("*") if path.is_file()
            }
            self.assertEqual(after, before)

    def test_partial_render_failure_preserves_previous_bundle(self):
        with TemporaryDirectory(prefix="rednote-atomic-") as tmp:
            output_dir = Path(tmp) / "output"
            pages_dir = output_dir / "pages"
            pages_dir.mkdir(parents=True)
            source_assets = renderer.collect_source_assets(self.article_spec, self.article_spec_path)
            previous_manifest = {
                "globalSpecSha256": renderer.global_spec_hash(self.article_spec),
                "sourceAssetsSha256": renderer.hash_json(source_assets),
                "pageCount": len(self.article_spec["pages"]),
                "pageMap": renderer.page_map_from_spec(self.article_spec),
            }
            (output_dir / "rednote.html").write_bytes(b"old-html")
            (output_dir / "contact-sheet.jpg").write_bytes(b"old-contact")
            (output_dir / "render-manifest.json").write_text(json.dumps(previous_manifest), encoding="utf-8")
            for page in range(1, len(self.article_spec["pages"]) + 1):
                (pages_dir / f"rednote_page_{page:02d}.jpg").write_bytes(f"old-{page}".encode())

            args = Namespace(
                spec=str(self.article_spec_path), output_dir=str(output_dir), pages="2",
                chrome=None, ffmpeg=None, ffprobe=None, makelive=None, timeout=1,
            )
            before = {
                path.relative_to(output_dir): path.read_bytes()
                for path in output_dir.rglob("*") if path.is_file()
            }
            with (
                patch.object(renderer, "find_chrome", return_value="chrome"),
                patch.object(renderer, "inspect_layout", side_effect=RuntimeError("synthetic render failure")),
            ):
                with self.assertRaisesRegex(RuntimeError, "synthetic render failure"):
                    renderer.run(args)

            after = {
                path.relative_to(output_dir): path.read_bytes()
                for path in output_dir.rglob("*") if path.is_file()
            }
            self.assertEqual(after, before)

    def test_full_publish_replaces_only_managed_outputs(self):
        with TemporaryDirectory(prefix="rednote-publish-") as tmp:
            root = Path(tmp)
            output_dir = root / "output"
            candidate_dir = root / "candidate"
            (output_dir / "pages").mkdir(parents=True)
            (candidate_dir / "pages").mkdir(parents=True)
            (output_dir / "pages" / "rednote_page_99.jpg").write_bytes(b"stale")
            (output_dir / "pages" / "notes.txt").write_bytes(b"keep")
            (output_dir / "rednote.html").write_bytes(b"old")
            (candidate_dir / "rednote.html").write_bytes(b"new")
            (candidate_dir / "contact-sheet.jpg").write_bytes(b"contact")
            (candidate_dir / "render-manifest.json").write_bytes(b"manifest")
            (candidate_dir / "pages" / "rednote_page_01.jpg").write_bytes(b"page")

            paths = renderer.managed_paths(candidate_dir) | renderer.managed_paths(output_dir)
            renderer.publish_managed_paths(candidate_dir, output_dir, paths)

            self.assertEqual((output_dir / "rednote.html").read_bytes(), b"new")
            self.assertEqual((output_dir / "pages" / "rednote_page_01.jpg").read_bytes(), b"page")
            self.assertFalse((output_dir / "pages" / "rednote_page_99.jpg").exists())
            self.assertEqual((output_dir / "pages" / "notes.txt").read_bytes(), b"keep")

    def test_publish_failure_restores_previous_managed_outputs(self):
        with TemporaryDirectory(prefix="rednote-publish-") as tmp:
            root = Path(tmp)
            output_dir = root / "output"
            candidate_dir = root / "candidate"
            output_dir.mkdir()
            candidate_dir.mkdir()
            (output_dir / "contact-sheet.jpg").write_bytes(b"old-contact")
            (output_dir / "rednote.html").write_bytes(b"old-html")
            (candidate_dir / "contact-sheet.jpg").write_bytes(b"new-contact")
            (candidate_dir / "rednote.html").write_bytes(b"new-html")
            original_replace = renderer.os.replace

            def fail_candidate_install(source, target):
                if Path(source) == candidate_dir / "rednote.html":
                    raise OSError("synthetic publish failure")
                return original_replace(source, target)

            with patch.object(renderer.os, "replace", side_effect=fail_candidate_install):
                with self.assertRaisesRegex(OSError, "synthetic publish failure"):
                    renderer.publish_managed_paths(candidate_dir, output_dir, renderer.managed_paths(candidate_dir))

            self.assertEqual((output_dir / "contact-sheet.jpg").read_bytes(), b"old-contact")
            self.assertEqual((output_dir / "rednote.html").read_bytes(), b"old-html")

    def test_partial_publish_replaces_selected_page_and_manifest_last(self):
        with TemporaryDirectory(prefix="rednote-publish-") as tmp:
            root = Path(tmp)
            output_dir = root / "output"
            candidate_dir = root / "candidate"
            (output_dir / "pages").mkdir(parents=True)
            (candidate_dir / "pages").mkdir(parents=True)
            for page in range(1, 4):
                (output_dir / "pages" / f"rednote_page_{page:02d}.jpg").write_bytes(
                    f"old-{page}".encode()
                )
            (output_dir / "rednote.html").write_bytes(b"old-html")
            (output_dir / "contact-sheet.jpg").write_bytes(b"old-contact")
            (output_dir / "render-manifest.json").write_bytes(b"old-manifest")
            (candidate_dir / "pages" / "rednote_page_02.jpg").write_bytes(b"new-2")
            (candidate_dir / "rednote.html").write_bytes(b"new-html")
            (candidate_dir / "contact-sheet.jpg").write_bytes(b"new-contact")
            (candidate_dir / "render-manifest.json").write_bytes(b"new-manifest")

            original_replace = renderer.os.replace
            installs = []

            def record_replace(source, target):
                source_path = Path(source)
                target_path = Path(target)
                if source_path.is_relative_to(candidate_dir) and ".publish-backup" not in source_path.parts:
                    installs.append(target_path.relative_to(output_dir))
                return original_replace(source, target)

            paths = renderer.partial_managed_paths(candidate_dir, [2])
            with patch.object(renderer.os, "replace", side_effect=record_replace):
                renderer.publish_managed_paths(candidate_dir, output_dir, paths)

            self.assertEqual((output_dir / "pages" / "rednote_page_01.jpg").read_bytes(), b"old-1")
            self.assertEqual((output_dir / "pages" / "rednote_page_02.jpg").read_bytes(), b"new-2")
            self.assertEqual((output_dir / "pages" / "rednote_page_03.jpg").read_bytes(), b"old-3")
            self.assertEqual((output_dir / "rednote.html").read_bytes(), b"new-html")
            self.assertEqual((output_dir / "contact-sheet.jpg").read_bytes(), b"new-contact")
            self.assertEqual((output_dir / "render-manifest.json").read_bytes(), b"new-manifest")
            self.assertEqual(installs[-1], Path("render-manifest.json"))

    def test_full_render_removes_stale_page_files_before_writing_current_pages(self):
        with TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            pages_dir = output_dir / "pages"
            pages_dir.mkdir()
            stale = pages_dir / "rednote_page_99.jpg"
            stale.write_bytes(b"stale")
            html_path = output_dir / "rednote.html"

            def fake_render_png(_chrome, _url, _target, path, _canvas, _timeout):
                path.write_bytes(b"png")

            def fake_png_to_jpg(_png, jpg, _size):
                jpg.write_bytes(b"jpg")

            def fake_contact_sheet(_files, path):
                path.write_bytes(b"contact")

            args = Namespace(pages=None, timeout=1)
            selected = list(range(1, len(self.article_spec["pages"]) + 1))
            with (
                patch.object(renderer, "render_png", side_effect=fake_render_png),
                patch.object(renderer, "png_to_jpg", side_effect=fake_png_to_jpg),
                patch.object(renderer, "build_contact_sheet", side_effect=fake_contact_sheet),
            ):
                files, _artifacts = renderer.render_static_targets(
                    args, self.article_spec, html_path, "chrome", output_dir, selected
                )

            self.assertFalse(stale.exists())
            self.assertEqual([path.name for path in files], [
                f"rednote_page_{page:02d}.jpg" for page in selected
            ])

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
