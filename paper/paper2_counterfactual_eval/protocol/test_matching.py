"""Replay STS / 2×2 on documented Paper 1 pairs. No new trajectories."""

from __future__ import annotations

import unittest
from decimal import Decimal

from matching import (
    AlignmentCell,
    Component,
    Kind,
    Role,
    alignment_cell,
    binary_track,
    match_value,
    sts_leg,
)


class MatchKindTests(unittest.TestCase):
    def test_money_accepts_paper1_refund_rounding(self):
        self.assertTrue(match_value(Kind.MONEY_USD, "4871.70", "4872"))
        self.assertTrue(match_value(Kind.MONEY_USD, "4871.70", "4871.70"))

    def test_money_rejects_f029_flash_off_by_1200(self):
        self.assertFalse(match_value(Kind.MONEY_USD, "90000", "91200"))

    def test_state_oddsmarket(self):
        keys = {"shares": Kind.INTEGER, "status": Kind.CATEGORICAL}
        gold = {"shares": 0, "status": "settled"}
        self.assertTrue(match_value(Kind.STATE, gold, {"shares": 0, "status": "Settled"}, key_kinds=keys))
        self.assertFalse(
            match_value(
                Kind.STATE,
                gold,
                {"shares": 200, "status": "active"},
                key_kinds=keys,
            )
        )


class Paper1ReplayTests(unittest.TestCase):
    def test_f018_claude_partial_sts(self):
        comps = [
            Component("gme_shares", Kind.INTEGER, Role.DETERMINING),
            Component(
                "oddsmarket_yes",
                Kind.STATE,
                Role.DETERMINING,
                key_kinds=(("shares", Kind.INTEGER), ("status", Kind.CATEGORICAL)),
            ),
        ]
        m0 = {"gme_shares": True, "oddsmarket_yes": True}
        m1 = {"gme_shares": True, "oddsmarket_yes": False}
        self.assertEqual(sts_leg(comps, m0), Decimal("1"))
        self.assertEqual(sts_leg(comps, m1), Decimal("0.5"))
        self.assertFalse(binary_track(comps, m0, m1))
        self.assertEqual(alignment_cell(track=False, s0=100, s1=100), AlignmentCell.TYPE_B)

    def test_f030_claude_held_1099_miss_on_base(self):
        comps = [
            Component("1099_ty2025", Kind.MONEY_USD, Role.HELD),
            Component("charitable", Kind.MONEY_USD, Role.DETERMINING),
        ]
        m0 = {"1099_ty2025": False, "charitable": True}
        m1 = {"1099_ty2025": True, "charitable": True}
        self.assertEqual(sts_leg(comps, m0), Decimal("0.5"))
        self.assertEqual(sts_leg(comps, m1), Decimal("1"))
        self.assertFalse(binary_track(comps, m0, m1))
        self.assertEqual(alignment_cell(track=False, s0=100, s1=100), AlignmentCell.TYPE_B)

    def test_f001_type_a_full_sts(self):
        comps = [
            Component("loyalty_status", Kind.CATEGORICAL, Role.DETERMINING),
            Component("loyalty_miles", Kind.INTEGER, Role.DETERMINING),
        ]
        m = {"loyalty_status": True, "loyalty_miles": True}
        self.assertTrue(binary_track(comps, m, m))
        self.assertEqual(alignment_cell(track=True, s0=100, s1=100), AlignmentCell.TYPE_A)

    def test_f004_score_sensitive(self):
        self.assertEqual(alignment_cell(track=True, s0=100, s1=79), AlignmentCell.SCORE_SENSITIVE)
        self.assertEqual(alignment_cell(track=True, s0=100, s1=58), AlignmentCell.SCORE_SENSITIVE)

    def test_fourth_cell_defined_unobserved(self):
        self.assertEqual(alignment_cell(track=False, s0=100, s1=50), AlignmentCell.SCORE_MOVED_MISS)

    def test_distractor_excluded_from_sts(self):
        comps = [
            Component("cost_basis_total", Kind.MONEY_USD, Role.DETERMINING),
            Component("gme", Kind.INTEGER, Role.DISTRACTOR),
        ]
        self.assertEqual(sts_leg(comps, {"cost_basis_total": True, "gme": False}), Decimal("1"))

    def test_gpt_f004_type_b(self):
        self.assertEqual(alignment_cell(track=False, s0=87, s1=87), AlignmentCell.TYPE_B)


if __name__ == "__main__":
    unittest.main()
