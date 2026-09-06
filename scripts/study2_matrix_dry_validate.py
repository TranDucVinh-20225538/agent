#!/usr/bin/env python3
"""Inspect-only dry validation for Study 2 matrix entrypoint (no legs / no QEMU)."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_AGENT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_AGENT_ROOT / "scripts"))
sys.path.insert(0, str(_AGENT_ROOT))

from study2_run_mypcbench import (  # noqa: E402
    FORBIDDEN_ENV,
    REQUIRED_KEY_PREFIX,
    STUDY2_FAMILIES,
    assert_study2_runtime_binding,
    resolve_family,
)
from generic_executor.family_config import FAMILY_CONFIGS  # noqa: E402
from generic_executor.openrouter_chat import OpenRouterChatCompletionsTransport  # noqa: E402


def enumerate_legs() -> list[dict]:
    au = json.loads((_AGENT_ROOT / "out/paper2_analysis_universe.json").read_text())
    co = json.loads((_AGENT_ROOT / "out/paper2_cell_order.json").read_text())
    multi = set(au["multi_i_both_pass"])
    legs = []
    for task in co["order"]:
        legs.append({"task": task, "leg": "G0", "cf": task, "probe": True})
        legs.append({"task": task, "leg": "G1", "cf": task, "probe": False})
        if task in multi:
            legs.append({"task": task, "leg": "G2", "cf": f"{task}-I2", "probe": False})
    return legs


def scan_scripts_for_forbidden() -> dict:
    """Static checks: Study 2 entrypoints must not invoke Gate0A/SMALL/native lanes."""
    files = [
        "scripts/study2_matrix.sh",
        "scripts/study2_matrix_lane.sh",
        "scripts/study2_exec_run.sh",
        "scripts/study2_run_mypcbench.py",
        "scripts/study2_bind_execution_key.sh",
    ]
    bad_patterns = [
        (r"paper2_gate0a_", "Gate0A smoke launcher reference"),
        (r"paper2_exec_small_lane", "SMALL lane launcher"),
        (r"paper2_exec_large_lane", "native LARGE lane launcher"),
        (r"OPENROUTER_API_KEY_SMALL(?!\s*=)", "SMALL key usage (assign/read)"),
    ]
    # Allow scrub/forbid mentions of SMALL in bind/bridge guards.
    allow_small_guard = {
        "scripts/study2_bind_execution_key.sh",
        "scripts/study2_run_mypcbench.py",
        "scripts/study2_exec_run.sh",
    }
    findings = []
    for rel in files:
        text = (_AGENT_ROOT / rel).read_text()
        for pat, label in bad_patterns:
            if re.search(pat, text):
                if "SMALL" in label and rel in allow_small_guard:
                    # only fail if it binds TO small rather than forbids
                    if "OPENROUTER_API_KEY=\"$OPENROUTER_API_KEY_SMALL\"" in text or \
                       "OPENROUTER_API_KEY='$OPENROUTER_API_KEY_SMALL'" in text:
                        findings.append({"file": rel, "issue": label, "pattern": pat})
                    continue
                findings.append({"file": rel, "issue": label, "pattern": pat})
    return {"files_scanned": files, "forbidden_hits": findings}


def main() -> int:
    out: dict = {
        "artifact": "study2_matrix_dry_validation",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "verdict": "FAIL",
        "checks": {},
    }

    # 1) Bind in a subshell via official bind script (does not launch matrix).
    bind_cmd = f"source {_AGENT_ROOT}/scripts/study2_bind_execution_key.sh && env"
    proc = subprocess.run(
        ["bash", "-lc", bind_cmd],
        cwd=str(_AGENT_ROOT / "external/MyPCBench-main"),
        capture_output=True,
        text=True,
        check=False,
    )
    env_map = {}
    for line in proc.stdout.splitlines():
        if "=" in line:
            k, _, v = line.partition("=")
            env_map[k] = v
    # Apply into this process for assert_study2_runtime_binding
    for k in list(os.environ.keys()):
        if k.startswith("OPENROUTER") or k in (
            "OPENAI_API_KEY",
            "OPENAI_BASE_URL",
            "ANTHROPIC_API_KEY",
            "STUDY2_EXECUTION_KEY_FINGERPRINT",
            "STUDY2_EXECUTION_KEY_SOURCE",
            "STUDY2_EXECUTION_LANE",
        ):
            os.environ.pop(k, None)
    for k, v in env_map.items():
        if k.startswith("OPENROUTER") or k in (
            "OPENAI_API_KEY",
            "OPENAI_BASE_URL",
            "STUDY2_EXECUTION_KEY_FINGERPRINT",
            "STUDY2_EXECUTION_KEY_SOURCE",
            "STUDY2_EXECUTION_LANE",
            "AGENT_ROOT",
        ):
            os.environ[k] = v

    try:
        binding = assert_study2_runtime_binding()
        out["checks"]["bind_008"] = {"ok": True, **binding}
    except SystemExit as e:
        out["checks"]["bind_008"] = {"ok": False, "error": str(e)}
        Path(_AGENT_ROOT / "out/study2_matrix_dry_validation.json").write_text(
            json.dumps(out, indent=2) + "\n"
        )
        print(json.dumps(out, indent=2))
        return 1

    # 2) Resolve each family → OpenRouter FAMILY_CONFIGS + transport class
    resolutions = []
    for fam in ("flash", "gpt", "claude"):
        os.environ["STUDY2_FAMILY"] = fam
        slug, cfg_key, model_id, out_slug = resolve_family(fam)
        cfg = FAMILY_CONFIGS[cfg_key]
        resolutions.append(
            {
                "family": slug,
                "config_key": cfg_key,
                "model_id": model_id,
                "out_slug": out_slug,
                "out_dir": f"results/paper2_exec/{out_slug}",
                "family_config_model": cfg.openrouter_model,
                "models_match": cfg.openrouter_model == model_id,
                "transport": OpenRouterChatCompletionsTransport.__name__,
                "agent_factory": "build_qwen_cuabash_agent + install_transport",
            }
        )
    out["checks"]["family_resolution"] = resolutions
    out["checks"]["family_order"] = ["flash", "gpt", "claude"]
    out["checks"]["all_models_match_config"] = all(r["models_match"] for r in resolutions)

    # 3) Enumerate legs
    legs = enumerate_legs()
    per_family = len(legs)
    total = per_family * 3
    out["checks"]["legs"] = {
        "per_family": per_family,
        "families": 3,
        "total_planned": total,
        "expect_total": 171,
        "first_five": legs[:5],
        "multiI_g2_count": sum(1 for x in legs if x["leg"] == "G2"),
    }

    # 4) Static forbidden launcher scan
    scan = scan_scripts_for_forbidden()
    out["checks"]["entrypoint_scan"] = scan

    # 5) Entry points exist
    entrypoints = {
        "study2_matrix.sh": (_AGENT_ROOT / "scripts/study2_matrix.sh").is_file(),
        "study2_matrix_lane.sh": (_AGENT_ROOT / "scripts/study2_matrix_lane.sh").is_file(),
        "study2_exec_run.sh": (_AGENT_ROOT / "scripts/study2_exec_run.sh").is_file(),
        "study2_run_mypcbench.py": (_AGENT_ROOT / "scripts/study2_run_mypcbench.py").is_file(),
        "study2_bind_execution_key.sh": (_AGENT_ROOT / "scripts/study2_bind_execution_key.sh").is_file(),
    }
    out["checks"]["entrypoints_present"] = entrypoints

    # 6) No study2 legs started
    root = _AGENT_ROOT / "results/paper2_exec"
    study2_dirs = sorted(str(p) for p in root.glob("study2*")) if root.exists() else []
    out["checks"]["no_matrix_legs_yet"] = {
        "study2_dirs": study2_dirs,
        "ok": len(study2_dirs) == 0,
    }

    ok = (
        out["checks"]["bind_008"]["ok"]
        and out["checks"]["all_models_match_config"]
        and total == 171
        and per_family == 57
        and not scan["forbidden_hits"]
        and all(entrypoints.values())
        and out["checks"]["no_matrix_legs_yet"]["ok"]
        and REQUIRED_KEY_PREFIX.startswith("sk-or-v1-008")
    )
    out["verdict"] = "PASS" if ok else "FAIL"
    out["forbidden_env_list"] = list(FORBIDDEN_ENV)
    out["note"] = "Dry validation only — matrix not launched."

    Path(_AGENT_ROOT / "out/study2_matrix_dry_validation.json").write_text(
        json.dumps(out, indent=2) + "\n"
    )
    print(json.dumps(out, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
