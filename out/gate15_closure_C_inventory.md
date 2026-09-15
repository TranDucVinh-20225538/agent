# Gate −1.5 Closure C — effective instrument dependency inventory

## Question

Does `out/paper2_harness_pin.json` include SHA256 identities for every
execution-critical external/runtime file that can affect **terminal-action
parsing** or **terminal-status classification**?

## Answer

**YES for the Paper-2 / Flash `qwen_cuabash` measurement chain**, via:

| Layer | Mechanism |
| --- | --- |
| Terminal-status classification (VALID_DONE) | **Option 2** — tracked SoT `scripts/paper2_traj_terminal.py` + callers (`paper2_exec_run.sh`, `resume_prep`, `canonical_audit_paper2.py`) |
| Terminal-action parsing / traj emission | **Option 1** — direct SHA256 pins of gitignored harness files listed below |

Vendor tree remains `.gitignore`d. Reproducibility is **pin-verify**, not
committing the full MyPCBench tree.

Verify: `python3 scripts/verify_paper2_harness_pin.py`

## Option 1 — directly pinned (gitignored upstream)

| Path | Role | Affects |
| --- | --- | --- |
| `external/MyPCBench-main/agent-harness/run_mypcbench.py` | react loop / traj writer | PREDICT_CRASH, EMPTY_XML, TOOL_CALL, `traj.action` |
| `external/MyPCBench-main/agent-harness/env.py` | QEMU env step | DONE/FAIL execution + `done` flag |
| `external/MyPCBench-main/agent-harness/agents/qwen_cua.py` | `qwen_cuabash` shim | agent entry / delegates parse |
| `…/vendored_paper_results/qwen35vl_agent.py` | `parse_response` | XML → DONE/FAIL |
| `…/vendored_paper_results/utils/qwen_vl_utils.py` | VL utils | Flash import path |
| `…/agents/prompts.py` | context prompt | Flash dependency (not classifier) |
| `…/agents/base.py` | base helpers | Gate −1 gap closed |
| `…/judge_results.py` | rubric judge entry | rubric only; **cannot** promote VALID_DONE |
| `…/utils/rubric_judge.py` | `rubric_bundle.json` builder | packaging only; missing bundle ≠ DONE |

## Option 2 — tracked remediation (measurement)

| Path | Role |
| --- | --- |
| `scripts/paper2_traj_terminal.py` | SoT classifier + fail-closed inspector |
| `scripts/canonical_audit_paper2.py` | offline reclass |
| `scripts/paper2_exec_run.sh` | runtime `cell_has_done` / checkpoint |
| `scripts/paper2_exec_resume_prep.sh` | resume backfill |
| `tests/test_paper2_terminal_parity.py` | Closure B parity |
| `scripts/verify_paper2_harness_pin.py` | pin drift check |

## Accepted residual (not a Gate −2 blocker for measurement)

| Dependency | Why residual | Risk to VALID_DONE |
| --- | --- | --- |
| Remainder of `external/MyPCBench-main/**` (QEMU drivers, tasks, images) | gitignored; not in Gate −1 terminal inventory | Does not define last-action classifier; pin drift of inventory files still detectable |

## Explicit non-claim

Pinning tracked wrappers alone would **not** be sufficient. This inventory
pins the underlying traj emitters / parsers (Option 1) **and** the tracked
classifier (Option 2).
