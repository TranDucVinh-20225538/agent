import unittest

from evidence_loss_audit import classify_links, discard_set
from evidence_loss_audit.adapters.p3 import from_found_and_survivors
from evidence_loss_audit.adapters.uv import K, group_screenshots_by_criterion
from evidence_loss_audit.lock import Episode, draw_episodes, render_lock_md
from evidence_loss_audit.sheets import build_stage1, build_stage2, majority_label


class DiscardTests(unittest.TestCase):
    def test_union_complement(self):
        self.assertEqual(discard_set(5, {0: [0, 1], 1: [1, 3]}), [2, 4])

    def test_empty_keep_discards_all(self):
        self.assertEqual(discard_set(3, {}), [0, 1, 2])

    def test_p3_only_collected_items_discard(self):
        self.assertEqual(from_found_and_survivors(4, found=[0, 1], survivors=[1]), [0])


class ChainTests(unittest.TestCase):
    def test_does_not_claim_loss_without_humans(self):
        row = classify_links(n_items=10, keep_cap=5, in_discard=True)
        self.assertTrue(row.opportunity)
        self.assertTrue(row.discard)
        self.assertIsNone(row.irrecoverable)
        self.assertEqual(row.note, "await_stage1")

    def test_irrecoverable_needs_both_labels(self):
        row = classify_links(
            n_items=10,
            keep_cap=5,
            in_discard=True,
            isolation="DECISIVE",
            equivalence="NOT_EQUIVALENT",
        )
        self.assertTrue(row.irrecoverable)
        self.assertFalse(row.redundant)

    def test_redundant_not_irrecoverable(self):
        row = classify_links(
            n_items=10,
            keep_cap=5,
            in_discard=True,
            isolation="DECISIVE",
            equivalence="EQUIVALENT",
        )
        self.assertFalse(row.irrecoverable)
        self.assertTrue(row.redundant)


class LockSheetTests(unittest.TestCase):
    def test_census_and_stable_controls(self):
        rows = [
            Episode("a", 12, 2),
            Episode("b", 8, 0),
            Episode("c", 11, 0),
            Episode("d", 3, 1),
        ]
        draw = draw_episodes(rows, keep_cap=5)
        self.assertTrue(draw.census)
        self.assertEqual([e.episode_id for e in draw.event], ["a", "d"])
        # nearest-median order: b (8) then c (11); cap 20 so both enter
        self.assertEqual([e.episode_id for e in draw.control], ["b", "c"])

    def test_lock_md_mentions_three_annotators(self):
        md = render_lock_md()
        self.assertIn("Annotators:** 3", md)
        self.assertIn("does not conclude", md)

    def test_stage1_hides_discard_on_sheet(self):
        key, ann = build_stage1(
            event=[{"episode_id": "t", "n_items": 4, "discard": [1, 2]}]
        )
        self.assertTrue(any(r["in_discard"] == 1 for r in key))
        self.assertEqual(set(ann[0]), {"item_id", "episode_id", "frame_index"})

    def test_stage2_foil_gallery(self):
        key, ann = build_stage2(
            decisive_targets=[
                {"episode_id": "t", "frame_index": 0, "in_discard": 1},
                {"episode_id": "t", "frame_index": 2, "in_discard": 0},
            ],
            keep_by_episode={"t": [2, 3]},
        )
        kinds = {r["gallery_kind"] for r in key}
        self.assertEqual(kinds, {"discard_vs_keep", "keep_foil"})
        self.assertNotIn("in_discard", ann[0])

    def test_majority(self):
        self.assertEqual(
            majority_label(["DECISIVE", "DECISIVE", "NOT_DECISIVE"]), "DECISIVE"
        )
        self.assertIsNone(majority_label(["UNCLEAR", "UNCLEAR", "DECISIVE"]))


class AdapterTests(unittest.TestCase):
    def test_uv_k_frozen(self):
        self.assertEqual(K, 5)
        scores = {
            0: {0: 9, 1: 1},
            1: {0: 8, 1: 2},
            2: {0: 7, 1: 3},
            3: {0: 6, 1: 4},
            4: {0: 5, 1: 9},
            5: {0: 4, 1: 8},
        }
        grouped = group_screenshots_by_criterion(scores, 2, max_k=K)
        self.assertEqual(len(grouped[0]), 5)
        self.assertNotIn(5, grouped[0])


if __name__ == "__main__":
    unittest.main()
