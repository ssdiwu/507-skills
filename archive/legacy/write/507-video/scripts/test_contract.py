#!/usr/bin/env python3
"""Regression checks for the conditional product-promo contract and routing boundary."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
PROFILE = ROOT / "references/product-promo-profile.md"


class VideoContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.skill = SKILL.read_text(encoding="utf-8")
        self.profile = PROFILE.read_text(encoding="utf-8")

    def test_product_promo_routes_to_a_conditional_profile_not_a_new_skill(self) -> None:
        self.assertIn("references/product-promo-profile.md", self.skill)
        self.assertIn("条件制作合同", self.skill)
        self.assertIn("不是新 skill", self.skill)

    def test_profile_keeps_breakdown_remix_and_release_outside_video(self) -> None:
        for boundary in ("507-breakdown", "507-remix", "不登录平台", "不上传", "不发布"):
            self.assertIn(boundary, self.skill + self.profile)

    def test_profile_declares_all_required_product_fields(self) -> None:
        expected = {
            "productTruthSource", "mustShowFeatures", "stateAndDataBoundary", "productVisualSource",
            "capturePlan", "featureShotMap", "audioCondition", "independentReview",
        }
        actual = set(re.findall(r"^\| `([A-Za-z][A-Za-z0-9]+)` \|", self.profile, flags=re.M))
        self.assertEqual(actual, expected)

    def test_final_render_requires_independent_review_and_current_studio_confirmation(self) -> None:
        self.assertIn("独立关键帧终检", self.skill)
        self.assertIn("Studio 明确确认", self.skill)
        self.assertIn("不渲染最终母版", self.skill)

    def test_product_claims_must_map_to_real_page_state(self) -> None:
        for requirement in ("must-show", "页面状态与证据", "不能暗示", "脱敏"):
            self.assertIn(requirement, self.profile)


if __name__ == "__main__":
    unittest.main()
