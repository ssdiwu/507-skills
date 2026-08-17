#!/usr/bin/env python3

import unittest

from check_prose import analyze, mask_non_prose


class CheckProseTests(unittest.TestCase):
    def test_masks_non_prose_without_changing_positions(self) -> None:
        text = """---
title: 不是事实，而是标题
---
# 不是标题，而是标题
> 不是引语，而是引语
正文从这里开始。
`不是代码，而是代码`
```text
不是代码块，而是代码块
```
[链接](https://example.com/a:b)
"""
        masked = mask_non_prose(text)
        self.assertEqual(len(masked), len(text))
        self.assertNotIn("不是事实", masked)
        self.assertNotIn("不是标题", masked)
        self.assertNotIn("不是引语", masked)
        self.assertNotIn("不是代码", masked)
        self.assertIn("正文从这里开始", masked)

    def test_single_comparison_does_not_trigger_density_warning(self) -> None:
        report = analyze("这不是排版问题，而是材料还不够。后面直接补上真实动作和结果。")
        self.assertNotIn("pivot-density", {finding.code for finding in report.findings})
        self.assertEqual(report.metrics["pivots"], 1)

    def test_clustered_comparisons_trigger_review(self) -> None:
        text = (
            "这不是排版问题，而是材料还不够。"
            "它并非不能工作，而是缺少真实输入。"
            "问题不在于字数，而在于每一段没有新东西。"
        )
        report = analyze(text)
        self.assertIn("pivot-density", {finding.code for finding in report.findings})

    def test_nominalization_is_reported_as_review(self) -> None:
        report = analyze("团队进行了流程优化，随后完成了对材料的整理。")
        self.assertIn("nominalization", {finding.code for finding in report.findings})

    def test_neutral_prose_has_no_findings(self) -> None:
        report = analyze("老周把药分进七个小格。走到门口，他又回来，把星期三那格打开看了一遍。")
        self.assertEqual(report.findings, [])


if __name__ == "__main__":
    unittest.main()
