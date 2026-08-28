#!/usr/bin/env python3
"""Offline checks for Phase B inject. Not a guest validation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import cf_file_patch  # noqa: E402
import cf_inject  # noqa: E402
import f004_dynamic  # noqa: E402

PHASE_B_IDS = [
    "retrieval-f001",
    "retrieval-f003",
    "retrieval-f016",
    "retrieval-f029",
    "retrieval-f030",
    "aggregation-f003",
    "aggregation-f018",
    "preference_inference-f004",
    "preference_inference-f018",
    "counterfactual-f004",
]


def test_load_all_ten() -> None:
    sources = {}
    for task_id in PHASE_B_IDS:
        spec, email = cf_inject.load_spec(task_id)
        assert spec.get("probe"), task_id
        assert email == "michael.scott@dundermifflin.com"
        sources[task_id] = spec.get("id")
    f004 = cf_inject.load_spec("preference_inference-f004")[0]
    assert f004.get("dynamic_patch") == "f004_hd_rank_flip"
    assert f004.get("patch") == []
    f029 = cf_inject.load_spec("retrieval-f029")[0]
    assert f029.get("file_patches")
    f030 = cf_inject.load_spec("retrieval-f030")[0]
    assert f030["expect"].get("probe_changes") is False
    # Stage 3 stub must not win over Phase B.
    assert f029["role"] == "phase_b_dual_channel"


def test_f029_file_from_probe() -> None:
    probe = json.loads(
        (ROOT / "results/probe-retrieval-f029/retrieval-f029.guest.json").read_text()
    )
    src = probe["files"]["~/Documents/Tax_2025/w2_summary.txt"]
    spec = cf_inject.load_spec("retrieval-f029")[0]
    patch = spec["file_patches"][0]
    out = cf_file_patch.apply_replacements(src, patch["replace"])
    cf_file_patch.check_hold_constant(out, patch["hold_constant"])
    assert "$90,000.00" in out
    assert "$18,000.00" in out
    assert "$142,000.00" not in out
    assert "Dunder Mifflin" in out


def test_f030_expect() -> None:
    spec = cf_inject.load_spec("retrieval-f030")[0]
    fails = cf_inject.evaluate_expect(
        spec,
        moved=False,
        after="[1099 unchanged]",
        files_before={"f": "1200"},
        files_after={"f": "1200"},
        extra_before=[{"result": "950"}],
        extra_after=[{"result": "100"}],
    )
    assert fails == []
    fails_bad = cf_inject.evaluate_expect(
        spec,
        moved=True,
        after="moved",
        files_before={},
        files_after={},
        extra_before=[{"result": "950"}],
        extra_after=[{"result": "950"}],
    )
    assert fails_bad


def test_f004_expect_tf_held() -> None:
    spec = cf_inject.load_spec("preference_inference-f004")[0]
    extra = [{"db": "tablefind.sqlite", "result": "Cooper 12"}]
    fails = cf_inject.evaluate_expect(
        spec,
        moved=True,
        after="Backyard 59",
        files_before={},
        files_after={},
        extra_before=extra,
        extra_after=extra,
    )
    assert fails == []
    fails_tf = cf_inject.evaluate_expect(
        spec,
        moved=True,
        after="Backyard 59",
        files_before={},
        files_after={},
        extra_before=extra,
        extra_after=[{"db": "tablefind.sqlite", "result": "changed"}],
    )
    assert any("extra probes" in f for f in fails_tf)


def main() -> int:
    cf_file_patch.self_test()
    f004_dynamic.self_test()
    test_load_all_ten()
    test_f029_file_from_probe()
    test_f030_expect()
    test_f004_expect_tf_held()
    print("test_phase_b_inject ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
