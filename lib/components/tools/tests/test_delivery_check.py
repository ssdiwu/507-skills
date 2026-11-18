import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "checks/delivery_check.py"


class DeliveryCheckTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / "任务"
        self.root.mkdir()
        self.record = self.root / "进度.md"
        self.product = self.root / "实际交付.md"
        self.check = {"type": "nonempty_file", "path": self.product.name}
        self.item = {"id": "稿件", "title": "交付稿件", "scope": "authorized", "checks": [self.check]}
        self.data = {"schema": 1, "decisions": {"确认": True}, "items": [self.item]}

    def write_record(self):
        self.record.write_text("原进度\n\n```delivery-json\n" + json.dumps(self.data, ensure_ascii=False) + "\n```\n")

    def invoke(self, code, record=None):
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "--task-root", str(self.root),
                                 "--record", record or self.record.name], cwd=self.root.parent,
                                capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        if code == 2:
            self.assertEqual(result.stdout, "")
            self.assertIn("error", json.loads(result.stderr))
        else:
            self.assertEqual(result.stderr, "")
            return json.loads(result.stdout)["items"]

    def test_real_artifact_and_decision_transitions(self):
        self.item["when"] = "确认"
        self.item["checks"].extend([{"type": "heading", "path": self.product.name, "level": 2, "equals": "结论"},
                                    {"type": "text_contains", "path": self.product.name, "value": "已核对"}])
        self.write_record()
        self.assertEqual(self.invoke(1)[0]["status"], "missing")
        self.product.write_text("   ## 结论 ### \n还有一项\n")
        self.assertEqual([row["status"] for row in self.invoke(1)[0]["checks"]],
                         ["satisfied", "satisfied", "missing"])
        self.product.write_text("## 结论\n已核对\n")
        before = {path: path.read_bytes() for path in self.root.iterdir()}
        self.assertEqual(self.invoke(0)[0]["status"], "satisfied")
        self.assertEqual({path: path.read_bytes() for path in self.root.iterdir()}, before)
        self.product.unlink()
        self.data["decisions"]["确认"] = False
        for scope in ("deferred", "cancelled", "needs_decision"):
            self.data["items"].append({**self.item, "id": scope, "scope": scope})
        self.write_record()
        rows = self.invoke(0)
        self.assertEqual([row["status"] for row in rows], ["waiting", "deferred", "cancelled", "needs_decision"])
        self.assertTrue(all(row["checks"] == [] for row in rows))

    def test_heading_ignores_examples_markup_and_wrong_level(self):
        self.item["checks"] = [{"type": "heading", "level": 2, "equals": "结论", "path": self.product.name}]
        self.write_record()
        self.product.write_text("---\n## 结论\n---\n正文 ## 结论\n### 结论\n## 结论二\n    ## 结论\n"
                                "> ## 结论\n````md\n```\n## 结论\n````\n~~~\n## 结论\n~~~\n"
                                "<!--\n## 结论\n-->\n<pre>\n## 结论\n</pre>\n<div>说明\n## 结论\n</div>\n")
        self.assertEqual(self.invoke(1)[0]["status"], "missing")

    def test_record_block_is_unique_complete_and_outside_examples(self):
        self.write_record()
        valid = self.record.read_text()
        example = "````md\n" + valid + "````\n"
        for raw in ("普通记录", example, valid + valid, valid[:-4], valid + "```delivery-json\n"):
            with self.subTest(raw=raw):
                self.record.write_text(raw)
                self.invoke(2)
        self.record.write_text(example + valid)
        self.assertEqual(self.invoke(1)[0]["status"], "missing")
        self.record.write_text("- 示例\n" + "".join("  " + line for line in valid.splitlines(keepends=True)) + "\n" + valid)
        self.assertEqual(self.invoke(1)[0]["status"], "missing")

    def test_record_text_cannot_satisfy_itself_from_declaration(self):
        self.item["checks"] = [{"type": "text_contains", "path": "./进度.md", "value": "最终交付"}]
        self.write_record()
        self.invoke(1)
        self.record.write_text(self.record.read_text() + "最终交付\n")
        self.invoke(0)

    def test_record_and_its_hard_link_cannot_prove_a_separate_nonempty_delivery(self):
        self.item["checks"] = [{"type": "nonempty_file", "path": "./进度.md"},
                               {"type": "nonempty_file", "path": "别名"},
                               {"type": "text_contains", "path": "别名", "value": "仅在声明内"}]
        self.write_record()
        os.link(self.record, self.root / "别名")
        self.assertEqual([row["status"] for row in self.invoke(1)[0]["checks"]], ["missing"] * 3)

    def test_invalid_records_and_checks(self):
        for update in ({"schema": True}, {"schema": 2}, {"decisions": {"是否": 1}}, {"items": {}},
                       {"items": []}, {"items": [self.item, self.item]}, {"items": [None]}):
            self.record.write_text("```delivery-json\n" + json.dumps({**self.data, **update}) + "\n```")
            self.invoke(2)
        for update in ({"id": ""}, {"scope": "done"}, {"when": "未知"}, {"checks": []},
                       {"checks": [{"type": "unknown"}]}, {"checks": [{**self.check, "value": "多余"}]},
                       {"checks": [{"type": "heading", "level": True, "equals": "标题", "path": "x"}]},
                       {"checks": [{"type": "text_contains", "path": "x", "value": " "}]}):
            self.data["items"] = [{**self.item, **update}]
            self.write_record()
            self.invoke(2)
        for raw in ("{", '{"schema": 1,"decisions":{},"items":[],"items":[]}'):
            self.record.write_text("```delivery-json\n" + raw + "\n```")
            self.invoke(2)

    def test_paths_and_symlinks_cannot_escape(self):
        outside = self.root.parent / "outside"
        outside.write_text("private")
        (self.root / "file-link").symlink_to(outside)
        (self.root / "dir-link").symlink_to(self.root.parent)
        (self.root / "dangling").symlink_to(self.root.parent / "absent")
        for path in ("../outside", str(outside), "dir-link/outside", "file-link", "dangling",
                     r"C:\outside", "C:outside", "sub/../inside"):
            with self.subTest(path=path):
                self.check["path"] = path
                self.write_record()
                self.invoke(2)
                self.invoke(2, path)
        self.assertEqual(outside.read_text(), "private")

    def test_binary_empty_absent_and_special_inputs(self):
        self.write_record()
        self.invoke(2, "absent")
        self.product.touch()
        self.invoke(1)
        self.product.write_bytes(b"\xff")
        self.invoke(0)
        self.item["checks"] = [{"type": "text_contains", "path": self.product.name, "value": "x"}]
        self.write_record()
        self.invoke(2)
        self.product.unlink()
        os.mkfifo(self.product)
        self.invoke(2)


if __name__ == "__main__":
    unittest.main()
