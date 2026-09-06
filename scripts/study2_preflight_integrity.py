#!/usr/bin/env python3
"""Study 2 Round-57 launch plumbing — integrity preflight before leg 1.

(A) Live OpenRouter balance for already-bound 008…9dd key.
(B) Code-level evidence of shared generic OpenRouter executor path (recorded, not a gate).
(C) Sealed task-universe / cell-order integrity vs locked launch manifest + hashes.

Fail closed → exit non-zero. Does not modify prereg/protocol/roster/universe/N/seed.
Does not start legs.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

_AGENT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_AGENT_ROOT / "scripts"))
sys.path.insert(0, str(_AGENT_ROOT))

from study2_run_mypcbench import (  # noqa: E402
    REQUIRED_KEY_PREFIX,
    STUDY2_FAMILIES,
    assert_study2_runtime_binding,
)
from generic_executor.executor import build_qwen_cuabash_agent  # noqa: E402
from generic_executor.family_config import FAMILY_CONFIGS  # noqa: E402
from generic_executor.openrouter_chat import OpenRouterChatCompletionsTransport  # noqa: E402
from generic_executor.transport import install_transport  # noqa: E402

MANIFEST_PATH = _AGENT_ROOT / "out/study2_launch_manifest.json"
PREREG_PATH = _AGENT_ROOT / "out/study2_phase4_preregistration.md"
CELL_ORDER_PATH = _AGENT_ROOT / "out/paper2_cell_order.json"
UNIVERSE_PATH = _AGENT_ROOT / "out/paper2_analysis_universe.json"
OUT_JSON = _AGENT_ROOT / "out/study2_round57_preflight.json"
OUT_MD = _AGENT_ROOT / "out/study2_round57_preflight.md"

# Funding envelope: mid Option L ~$348; require headroom above low envelope.
MIN_REMAINING_USD = float(os.environ.get("STUDY2_MIN_REMAINING_USD", "100"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_A_balance() -> dict:
    binding = assert_study2_runtime_binding()
    key = os.environ["OPENROUTER_API_KEY"]
    if not key.startswith(REQUIRED_KEY_PREFIX):
        raise SystemExit(f"A_FAIL: key prefix not {REQUIRED_KEY_PREFIX}")
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/key",
        headers={"Authorization": f"Bearer {key}"},
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        data = json.load(resp).get("data", {})
    remaining = float(data.get("limit_remaining") or 0)
    label = data.get("label") or ""
    ok = (
        remaining >= MIN_REMAINING_USD
        and "008" in (binding.get("fingerprint_masked") or "")
        and ("008" in label or label.startswith("sk-or-v1-008"))
    )
    return {
        "ok": ok,
        "fingerprint_masked": binding["fingerprint_masked"],
        "live_label": label,
        "limit": data.get("limit"),
        "limit_remaining": remaining,
        "usage": data.get("usage"),
        "min_required_usd": MIN_REMAINING_USD,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def check_B_shared_executor_evidence() -> dict:
    """Record-only: all three locked families share the same bridge factory/transport."""
    evidence = []
    for fam, (cfg_key, model_id, out_slug) in STUDY2_FAMILIES.items():
        cfg = FAMILY_CONFIGS[cfg_key]
        evidence.append(
            {
                "family": fam,
                "model_id": model_id,
                "out_slug": out_slug,
                "bridge_module": "scripts/study2_run_mypcbench.py",
                "agent_factory": f"{build_qwen_cuabash_agent.__module__}.{build_qwen_cuabash_agent.__name__}",
                "transport_class": f"{OpenRouterChatCompletionsTransport.__module__}.{OpenRouterChatCompletionsTransport.__name__}",
                "install_transport": f"{install_transport.__module__}.{install_transport.__name__}",
                "family_config_model": cfg.openrouter_model,
                "models_match": cfg.openrouter_model == model_id,
            }
        )
    shared_factory = len({e["agent_factory"] for e in evidence}) == 1
    shared_transport = len({e["transport_class"] for e in evidence}) == 1
    shared_bridge = len({e["bridge_module"] for e in evidence}) == 1
    return {
        "ok": shared_factory and shared_transport and shared_bridge and all(e["models_match"] for e in evidence),
        "gate": False,  # not an approval gate — evidence only
        "families": evidence,
        "note": "All Study 2 families use study2_run_mypcbench → qwen_cuabash + OpenRouterChatCompletionsTransport.",
    }


def check_C_universe_order() -> dict:
    if not MANIFEST_PATH.is_file():
        raise SystemExit("C_FAIL: missing out/study2_launch_manifest.json")
    manifest = json.loads(MANIFEST_PATH.read_text())
    locked = manifest.get("phase4_preregistration") or {}
    matrix = manifest.get("matrix") or {}
    models = manifest.get("models") or []

    prereg_sha = _sha256(PREREG_PATH)
    cell_sha = _sha256(CELL_ORDER_PATH)
    uni_sha = _sha256(UNIVERSE_PATH)
    co = json.loads(CELL_ORDER_PATH.read_text())
    au = json.loads(UNIVERSE_PATH.read_text())

    order = co.get("order") or []
    multi = set(au.get("multi_i_both_pass") or [])
    legs = []
    for task in order:
        legs.append((task, "G0"))
        legs.append((task, "G1"))
        if task in multi:
            legs.append((task, "G2"))

    expect = {
        "T": 25,
        "n_multiI": 7,
        "N_fam": 57,
        "M": 3,
        "L_total": 171,
        "seed": 20260904,
    }
    issues = []
    if locked.get("sha256") != prereg_sha:
        issues.append(f"prereg sha mismatch manifest={locked.get('sha256')} live={prereg_sha}")
    if matrix.get("T") != expect["T"] or au.get("n_tasks") != expect["T"] or len(order) != expect["T"]:
        issues.append("T!=25")
    if matrix.get("n_multiI") != expect["n_multiI"] or au.get("n_multi_i_both_pass") != expect["n_multiI"]:
        issues.append("multiI!=7")
    if matrix.get("N_fam") != expect["N_fam"] or len(legs) != expect["N_fam"]:
        issues.append(f"N_fam!=57 (legs={len(legs)})")
    if matrix.get("L_total") != expect["L_total"] or len(legs) * 3 != expect["L_total"]:
        issues.append("L_total!=171")
    if co.get("PAPER2_EXEC_SEED") != expect["seed"] or str(matrix.get("seed_carryforward")) != str(expect["seed"]):
        issues.append("seed!=20260904")
    if set(order) != set(au.get("tasks") or []):
        issues.append("cell_order tasks != universe.tasks")
    want_models = [
        ("qwen/qwen3.8-flash", "results/paper2_exec/study2-flash"),
        ("openai/gpt-5.5", "results/paper2_exec/study2-gpt"),
        ("anthropic/claude-opus-4.6", "results/paper2_exec/study2-claude"),
    ]
    got_models = [(m.get("model_id"), m.get("out_dir")) for m in models]
    if got_models != want_models:
        issues.append(f"roster/out mismatch: {got_models}")

    # First locked task unit must be retrieval-f010
    if not order or order[0] != "retrieval-f010":
        issues.append(f"first task != retrieval-f010 ({order[:1]})")

    return {
        "ok": not issues,
        "issues": issues,
        "hashes": {
            "prereg_sha256": prereg_sha,
            "manifest_prereg_sha256": locked.get("sha256"),
            "cell_order_sha256": cell_sha,
            "universe_sha256": uni_sha,
        },
        "matrix": {
            "T": len(order),
            "n_multiI": len(multi),
            "N_fam": len(legs),
            "L_total": len(legs) * 3,
            "seed": co.get("PAPER2_EXEC_SEED"),
            "first_task": order[0] if order else None,
            "first_legs": [f"{t}:{g}" for t, g in legs[:5]],
        },
        "manifest_path": str(MANIFEST_PATH.relative_to(_AGENT_ROOT)),
    }


def main() -> int:
    report = {
        "artifact": "study2_round57_preflight",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "verdict": "FAIL",
        "A_balance": None,
        "B_shared_executor_evidence": None,
        "C_universe_order": None,
    }
    try:
        report["A_balance"] = check_A_balance()
        report["B_shared_executor_evidence"] = check_B_shared_executor_evidence()
        report["C_universe_order"] = check_C_universe_order()
    except SystemExit as e:
        report["error"] = str(e)
        OUT_JSON.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
        return 2
    except Exception as e:
        report["error"] = f"{type(e).__name__}: {e}"
        OUT_JSON.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
        return 2

    a_ok = bool(report["A_balance"] and report["A_balance"]["ok"])
    c_ok = bool(report["C_universe_order"] and report["C_universe_order"]["ok"])
    # B is evidence-only; still record ok but do not gate launch on it alone.
    b_ok = bool(report["B_shared_executor_evidence"] and report["B_shared_executor_evidence"]["ok"])
    report["verdict"] = "PASS" if (a_ok and c_ok and b_ok) else "FAIL"
    report["launch_gates"] = {"A": a_ok, "C": c_ok, "B_evidence_only": b_ok}

    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n")
    lines = [
        "# Study 2 Round-57 preflight (launch plumbing)",
        "",
        f"**Verdict:** **{report['verdict']}**",
        f"**Checked at (UTC):** {report['checked_at_utc']}",
        "",
        "## A — Live balance (008…9dd)",
        f"- ok: `{a_ok}`",
        f"- fingerprint: `{report['A_balance'].get('fingerprint_masked')}`",
        f"- limit_remaining: `{report['A_balance'].get('limit_remaining')}`",
        f"- min_required_usd: `{report['A_balance'].get('min_required_usd')}`",
        "",
        "## B — Shared executor evidence (not an approval gate)",
        f"- ok: `{b_ok}`",
        f"- {report['B_shared_executor_evidence'].get('note')}",
        "",
        "## C — Sealed universe / order vs locked manifest",
        f"- ok: `{c_ok}`",
        f"- issues: `{report['C_universe_order'].get('issues')}`",
        f"- prereg sha: `{report['C_universe_order']['hashes']['prereg_sha256']}`",
        f"- matrix: `{json.dumps(report['C_universe_order']['matrix'])}`",
        "",
        "JSON twin: `out/study2_round57_preflight.json`",
        "",
    ]
    OUT_MD.write_text("\n".join(lines))
    print(json.dumps(report, indent=2))
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
