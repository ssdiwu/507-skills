#!/usr/bin/env python3

import unittest

from check_spoken import analyze, mask_non_spoken


class CheckSpokenTests(unittest.TestCase):
    def test_masks_metadata_code_headings_and_section_ids(self) -> None:
        text = """---
title: 测试
---
# 第一页
[SECTION:hook]
这里开始说话。
```text
这段不说出口。
```
"""
        masked = mask_non_spoken(text)
        self.assertEqual(len(masked), len(text))
        self.assertNotIn("第一页", masked)
        self.assertNotIn("SECTION", masked)
        self.assertNotIn("这段不说出口", masked)
        self.assertIn("这里开始说话", masked)

    def test_long_sentence_triggers_breath_review(self) -> None:
        text = "这句话把背景条件参与角色时间范围失败结果和下一步动作全都挤在一起，听众听到最后已经很难记住开头是谁在做什么。"
        report = analyze(text)
        self.assertIn("long-breath", {finding.code for finding in report.findings})

    def test_clustered_comparisons_trigger_review(self) -> None:
        text = (
            "这不是功能问题，而是输入不够。"
            "它并非不会回答，而是没有项目材料。"
            "问题不在于模型，而在于协作过程。"
        )
        report = analyze(text)
        self.assertIn("pivot-density", {finding.code for finding in report.findings})

    def test_written_meta_and_pronunciation_are_reported(self) -> None:
        report = analyze("本文将说明 AI 如何接入 SOP，当前版本是 v1.2，成功率达到 80%。")
        codes = {finding.code for finding in report.findings}
        self.assertIn("written-meta", codes)
        self.assertIn("pronunciation-candidates", codes)
        self.assertEqual(report.metrics["pronunciation_candidates"], 4)

    def test_short_concrete_spoken_text_has_no_style_findings(self) -> None:
        report = analyze("这辆车已经还回门店。系统写回时间和负责人，人只需要确认异常。")
        self.assertEqual(report.findings, [])


if __name__ == "__main__":
    unittest.main()
