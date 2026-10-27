from __future__ import annotations

import base64
import io
import json
import os
import shutil
import sys
import tempfile
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from render_rednote import find_chrome  # noqa: E402
from migrate_rednote_project import migrate  # noqa: E402
from serve_rednote import (  # noqa: E402
    ProjectState,
    atomic_write,
    compile_project_headless,
    export_project,
    font_set_identity,
    handler_factory,
    store_uploaded_image,
)


class RuntimeStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="rednote-runtime-test-")
        self.root = Path(self.temporary.name)
        self.runtime = SCRIPT_DIR.parent / "runtime"
        self.source = SCRIPT_DIR / "fixtures" / "sample-runtime-content.md"
        assets = self.root / "assets"
        assets.mkdir()
        shutil.copy2(SCRIPT_DIR / "fixtures" / "sample.svg", assets / "sample.svg")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_project_state_seeds_files_without_overwriting(self) -> None:
        state = ProjectState(self.root, self.runtime, self.source, None)
        self.assertIn("真实 DOM 分页测试", (self.root / "content.md").read_text(encoding="utf-8"))
        plan = json.loads((self.root / "visual-plan.json").read_text(encoding="utf-8"))
        self.assertEqual(plan["designLanguage"], "bold-statement")
        self.assertEqual(plan["typography"]["fontFamily"], "source-han-sans")
        self.assertEqual(plan["typography"]["characterWidth"], 1.0)
        self.assertRegex(font_set_identity(self.runtime), r"^source-han-cn-ofl-v1:[0-9a-f]{64}$")
        atomic_write(self.root / "content.md", "# 用户改动\n")
        ProjectState(self.root, self.runtime, self.source, None)
        self.assertEqual((self.root / "content.md").read_text(encoding="utf-8"), "# 用户改动\n")
        with self.assertRaises(PermissionError):
            state.safe_project_path("../outside.txt")

    def test_legacy_article_migrates_to_markdown_and_three_axis_plan(self) -> None:
        spec = json.loads((SCRIPT_DIR / "fixtures" / "sample-article-project.json").read_text(encoding="utf-8"))
        content, plan = migrate(spec)
        self.assertTrue(content.startswith("# "))
        self.assertIn("##", content)
        self.assertIn("![", content)
        self.assertEqual(plan["mode"], "article")
        self.assertIn(plan["designLanguage"], {"editorial-archive", "precision-modern", "bold-statement"})

    def test_direct_html_explains_launcher_and_launcher_is_executable(self) -> None:
        index = (self.runtime / "index.html").read_text(encoding="utf-8")
        self.assertIn('./dist/app.js', index)
        self.assertIn('file-mode-help', index)
        launcher = SCRIPT_DIR.parent / "open-rednote.command"
        self.assertTrue(os.access(launcher, os.X_OK))
        self.assertIn('serve_rednote.py', launcher.read_text(encoding="utf-8"))

    def test_uploaded_image_is_verified_and_stored_under_assets(self) -> None:
        state = ProjectState(self.root, self.runtime, self.source, None)
        buffer = io.BytesIO()
        Image.new("RGB", (12, 8), "#cc4422").save(buffer, "PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode()
        result = store_uploaded_image(state, {"fileName": "封面 图片.png", "dataUrl": f"data:image/png;base64,{encoded}"})
        self.assertTrue(result["path"].startswith("assets/封面-图片-"))
        self.assertTrue((self.root / result["path"]).is_file())
        self.assertRegex(result["assetSetSha256"], r"^[0-9a-f]{64}$")
        self.assertEqual((result["width"], result["height"]), (12, 8))
        with self.assertRaisesRegex(ValueError, "只支持"):
            store_uploaded_image(state, {"fileName": "bad.svg", "dataUrl": "data:image/svg+xml;base64,PHN2Zz4="})
        animated = io.BytesIO()
        frames = [Image.new("RGB", (8, 8), color) for color in ("#cc4422", "#2244cc")]
        frames[0].save(animated, "GIF", save_all=True, append_images=frames[1:], duration=100, loop=0)
        animated_data = base64.b64encode(animated.getvalue()).decode()
        with self.assertRaisesRegex(ValueError, "不支持动态图片"):
            store_uploaded_image(state, {"fileName": "animated.gif", "dataUrl": f"data:image/gif;base64,{animated_data}"})


class RuntimeBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            cls.chrome = find_chrome(None)
        except SystemExit as exc:
            raise unittest.SkipTest(str(exc)) from exc

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="rednote-runtime-browser-")
        self.root = Path(self.temporary.name)
        assets = self.root / "assets"
        assets.mkdir()
        shutil.copy2(SCRIPT_DIR / "fixtures" / "sample.svg", assets / "sample.svg")
        self.state = ProjectState(
            self.root,
            SCRIPT_DIR.parent / "runtime",
            SCRIPT_DIR / "fixtures" / "sample-runtime-content.md",
            self.chrome,
        )
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), handler_factory(self.state))
        self.state.base_url = f"http://127.0.0.1:{self.server.server_address[1]}"
        self.thread = threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.1}, daemon=True)
        self.thread.start()

    def tearDown(self) -> None:
        self.server.shutdown()
        self.thread.join(timeout=3)
        self.server.server_close()
        self.temporary.cleanup()

    def test_compile_and_export_use_same_three_by_four_runtime(self) -> None:
        paged = compile_project_headless(self.state)
        self.assertEqual(paged["status"], "compiled")
        self.assertEqual(paged["canvas"]["width"], 1500)
        self.assertEqual(paged["canvas"]["height"], 2000)
        self.assertRegex(paged["inputs"]["runtimeSha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(paged["inputs"]["assetSetSha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(paged["inputs"]["fontSet"], r"^source-han-cn-ofl-v1:[0-9a-f]{64}$")
        self.assertGreaterEqual(paged["pageCount"], 3)
        self.assertTrue(all(not page["validation"]["overflow"] for page in paged["pages"]))
        kinds = {fragment["type"] for page in paged["pages"] for fragment in page["fragments"]}
        self.assertTrue({"table", "diagram", "media"}.issubset(kinds))
        self.assertIn("forced", {page["break"]["kind"] for page in paged["pages"]})
        self.assertIn("https://example.com/reference", "\n".join(page["contentText"] for page in paged["pages"]))

        result = export_project(self.state, "png")
        self.assertEqual(result["pageCount"], paged["pageCount"])
        page_files = sorted((self.root / "pages").glob("*.png"))
        self.assertEqual(len(page_files), paged["pageCount"])
        with Image.open(page_files[-1]) as image:
            self.assertEqual(image.size, (1500, 2000))
        manifest = json.loads((self.root / "render-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["pageCount"], paged["pageCount"])
        self.assertEqual(manifest["canvas"], [1500, 2000])
        self.assertIn("Google Chrome", manifest["tools"]["chrome"])
        self.assertIn("pages/rednote_page_01.png", (self.root / "rednote.html").read_text(encoding="utf-8"))
        atomic_write(self.root / "content.md", (self.root / "content.md").read_text(encoding="utf-8") + "\n外部变化\n")
        with self.assertRaisesRegex(ValueError, "分页已过期"):
            export_project(self.state, "png")

    def test_upload_endpoint_keeps_image_inside_project_assets(self) -> None:
        buffer = io.BytesIO()
        Image.new("RGB", (24, 16), "#4466cc").save(buffer, "PNG")
        body = json.dumps({
            "fileName": "正文图片.png",
            "dataUrl": f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}",
        }, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            f"{self.state.base_url}/api/upload-image",
            data=body,
            method="POST",
            headers={"Content-Type": "application/json", "X-Rednote-Token": self.state.token},
        )
        with urllib.request.urlopen(request) as response:
            result = json.loads(response.read().decode("utf-8"))
        self.assertTrue(result["path"].startswith("assets/正文图片-"))
        self.assertTrue((self.root / result["path"]).is_file())
        self.assertEqual(result["alt"], "正文图片")

    def test_summary_requires_one_heading_and_one_page_per_section(self) -> None:
        plan = json.loads((self.root / "visual-plan.json").read_text(encoding="utf-8"))
        plan["mode"] = "summary"
        atomic_write(self.root / "visual-plan.json", json.dumps(plan, ensure_ascii=False, indent=2) + "\n")
        summary = (SCRIPT_DIR / "fixtures" / "sample-runtime-summary.md").read_text(encoding="utf-8")
        atomic_write(self.root / "content.md", summary)
        paged = compile_project_headless(self.state)
        self.assertEqual(paged["mode"], "summary")
        self.assertEqual(paged["status"], "compiled")
        self.assertEqual(paged["validationIssues"], [])
        self.assertEqual(paged["pageCount"], 3)

        invalid = "# 摘要\n\n## 观点一\n\n正文。\n\n## 观点二\n\n正文。\n"
        atomic_write(self.root / "content.md", invalid)
        with self.assertRaisesRegex(RuntimeError, "无界面分页编译失败"):
            compile_project_headless(self.state)

    def test_bundled_serif_font_and_character_width_compile_in_final_dom(self) -> None:
        plan = json.loads((self.root / "visual-plan.json").read_text(encoding="utf-8"))
        plan["typography"]["fontFamily"] = "source-han-serif"
        plan["typography"]["characterWidth"] = 0.94
        atomic_write(self.root / "visual-plan.json", json.dumps(plan, ensure_ascii=False, indent=2) + "\n")
        narrow = compile_project_headless(self.state)
        self.assertEqual(narrow["status"], "compiled")
        self.assertRegex(narrow["inputs"]["fontSet"], r"^source-han-cn-ofl-v1:[0-9a-f]{64}$")

        plan["typography"]["characterWidth"] = 1.08
        atomic_write(self.root / "visual-plan.json", json.dumps(plan, ensure_ascii=False, indent=2) + "\n")
        wide = compile_project_headless(self.state)
        self.assertEqual(wide["status"], "compiled")
        self.assertNotEqual(narrow["inputs"]["visualPlanSha256"], wide["inputs"]["visualPlanSha256"])


if __name__ == "__main__":
    unittest.main()
