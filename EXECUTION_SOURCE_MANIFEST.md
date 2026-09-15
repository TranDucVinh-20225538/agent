# EXECUTION_SOURCE_MANIFEST.md — Gate −1 Execution Provenance

**Host:** `node30`  
**AGENT_ROOT (absolute):** `/mnt/data2/Vinh/agent`  
**Investigation date (UTC):** 2026-09-06  
**STOP:** No generic-agent implementation, no Gate −2, no API runs, no semantic patches in this gate.

---

## 1. Runtime source tree

### Evidence

| Claim | Evidence |
| --- | --- |
| Host | `hostname` → `node30` |
| Working directory / AGENT_ROOT | `/mnt/data2/Vinh/agent` |
| Launcher default | Every Paper-2 script: `A="${AGENT_ROOT:-$(cd "$(dirname …)/.." && pwd)}"` → resolves to `/mnt/data2/Vinh/agent` when unset |
| Flash lane log | `results/paper2_exec_qwen38-flash.log` line 1–3: `HEAD=68f30ea LANE=SMALL MODEL=qwen/qwen3.8-flash AGENT=qwen_cuabash` · `OUT_ROOT=/mnt/data2/Vinh/agent/results/paper2_exec/qwen38-flash` · harness under `/mnt/data2/Vinh/agent/external/MyPCBench-main/…` |
| Current git HEAD | `64054a1a6f19088d788be3b383d3076d12e37406` (`phase-a-results`, tracks `origin/phase-a-results`) |
| Flash start HEAD | `68f30ea` (ancestor of current HEAD) |
| Working tree (non-result noise) | Modified: `scripts/paper2_exec_large_lane.sh` (uncommitted). Untracked: many `results/*`, `.venv-vllm/`, `GENERIC_AGENT_INVARIANTS.md`, gate0 dirs, etc. |
| **Critical:** harness tree | Path `/mnt/data2/Vinh/agent/external/MyPCBench-main/` is **`gitignore`d** (`.gitignore` line `external/`). **Not** a nested git repo (no `external/MyPCBench-main/.git`). **Not** listed by `git ls-files`. |

Paper-2 Qwen/Flash executions therefore ran a **hybrid** instrument:

- **Tracked** Paper-2 orchestration scripts under `/mnt/data2/Vinh/agent/scripts/`
- **Untracked / gitignored** MyPCBench harness under `/mnt/data2/Vinh/agent/external/MyPCBench-main/agent-harness/`

mtime evidence that the ignored harness was stable through Flash (Flash window ≈ 2026-09-05T00:54Z → ~2026-09-06T03:17Z):

| File | mtime (UTC) |
| --- | --- |
| `…/run_mypcbench.py` | 2026-09-02 05:56:43 |
| `…/agents/qwen_cua.py` | 2026-09-02 05:56:43 |
| `…/env.py` | 2026-08-26 08:10:17 |
| `…/vendored_paper_results/qwen35vl_agent.py` | 2026-08-21 01:15:03 |

`scripts/paper2_exec_run.sh` on disk was later rewritten (mtime 2026-09-06 04:28; commits `c665058`, `55fb05c` after Flash start). The **running Flash bash process** started at `68f30ea` and retained that process’s loaded `cell_has_done` / checkpoint logic; the buggy regex already existed at `68f30ea` (see §3).

---

## 2. Execution call chain (Qwen / Flash Paper-2)

```
[1] scripts/paper2_exec_small_9b_then_flash.sh
        │  (or wait_9b_then_flash → small_lane)
        ▼
[2] scripts/paper2_exec_small_lane.sh
        │  binds OPENROUTER_API_KEY_SMALL → OPENROUTER_API_KEY / OPENAI_*
        │  export AGENT_ROOT=/mnt/data2/Vinh/agent
        ▼
[3] scripts/paper2_exec_run.sh          # outer Paper-2 runner
        │  walks out/paper2_cell_order.json (57 legs)
        │  pins task JSON → external/.../tasks/cf_one
        │  run_agent → python run_mypcbench.py
        │  judge_dir → judge_results.py
        │  archive_cell → results/paper2_exec/<slug>/…
        │  cell_has_done → write_leg_checkpoint → CHECKPOINT.jsonl
        ▼
[4] external/MyPCBench-main/agent-harness/run_mypcbench.py
        │  get_agent(qwen_cuabash) → QwenOSWorldAgent(enable_bash=True)
        │  run_single_example: predict → env.step → traj.jsonl
        │  writes result.txt = 1.0 if loop returns without raise  (**completion ≠ DONE action**)
        ▼
[5] agents/qwen_cua.py :: QwenOSWorldAgent / _Qwen35VLPatched
        │  system addenda: MYPCBENCH_CONTEXT + bash tool text
        │  bash XML extract → env._execute_command
        ▼
[6] agents/vendored_paper_results/qwen35vl_agent.py :: Qwen35VLAgent
        │  system prompt + tools_def JSON
        │  observation: process_image → messages
        │  call_llm (OpenAI-compatible → OpenRouter)
        │  parse_response (XML computer_use → pyautogui / DONE / FAIL / WAIT)
        ▼
[7] agents/vendored_paper_results/utils/qwen_vl_utils.py :: smart_resize
        ▼
[8] env.py :: MyPCBenchEnv
        │  QEMU boot, screenshot HTTP, _execute_pyautogui, _execute_command
        │  step("DONE"|"FAIL"|"WAIT"|pyautogui) → obs, done flag
        ▼
[9] scripts/cf_inject.py (via MYPCBENCH_CF_* env during env.reset path)
        ▼
[10] agent-harness/judge_results.py (post-leg rubric; separate from DONE status)
```

### Layer → function map (requested list)

| # | Responsibility | Absolute path | Symbol |
| --- | --- | --- | --- |
| 1 | Launcher / lane | `/mnt/data2/Vinh/agent/scripts/paper2_exec_small_lane.sh` (+ `paper2_exec_small_9b_then_flash.sh`, `paper2_exec_wait_9b_then_flash.sh`) | shell entry |
| 2 | Outer execution runner | `/mnt/data2/Vinh/agent/scripts/paper2_exec_run.sh` | main loop, `run_agent`, `write_leg_checkpoint` |
| 3 | Model/agent loop | `…/agent-harness/run_mypcbench.py` | `run_single_example` |
| 4 | System prompt + task injection | `…/qwen35vl_agent.py` `predict` system string; `…/qwen_cua.py` `_Qwen35VLPatched.call_llm`; `…/prompts.py` `build_mypcbench_context`; task instruction from pinned JSON | |
| 5 | XML/action parser | `…/qwen35vl_agent.py` | `parse_response` |
| 6 | Parsed action representation | list of pyautogui strings / `DONE`/`FAIL`/`WAIT`; traj `action` field | |
| 7 | QEMU / computer executor | `…/env.py` | `MyPCBenchEnv.step`, `_execute_pyautogui` |
| 8 | Screenshot / observation | `…/env.py` `_get_screenshot` / `_get_obs`; agent `process_image` | |
| 9 | Terminal-action classification (agent) | `parse_response` → `DONE`/`FAIL`/`WAIT`; runner empty/TOOL_CALL/EMPTY_XML | |
| 10 | `has_done_action` | **`scripts/paper2_exec_run.sh`** only (not in harness agent). Computed in `write_leg_checkpoint` from traj grep; written into `paper2_leg_finished.json` + `CHECKPOINT.jsonl` | |
| 11 | Checkpoint writing | `scripts/paper2_exec_run.sh` `write_leg_checkpoint` → append `CHECKPOINT.jsonl` | |
| 12 | Leg completion status | `paper2_exec_run.sh`: if `cell_has_done` → status **`DONE`**; elif has steps → **`TERMINAL_FAIL`**; else **`BOOT_NO_RESULT`** | |

---

## 3. False-DONE provenance (exact)

### Observed examples (Flash archive on node30)

| task | leg | CHECKPOINT `status` | `has_done_action` | Last traj `action` | Last traj `done` |
| --- | --- | --- | --- | --- | --- |
| aggregation-f036 | G0 | DONE | true | `PREDICT_CRASH` | true |
| preference_inference-f014 | G0 | DONE | true | `PREDICT_CRASH` | true |
| contradiction-f006 | G1 | DONE | true | `PREDICT_CRASH` | true |
| aggregation-f040 | G2 | DONE | true | `FAIL` | true |

Flash unique legs: **27** checkpointed as `DONE`, of which **23** have `"action": "DONE"` and **4** are false-DONE as above. 9B: **1** true DONE, **0** false-DONE in this scan.

### Causal chain (runtime)

```
final model response / crash
    │
    ▼
[A] Agent / runner writes traj.jsonl row
    • Normal FAIL: env.step("FAIL") → traj action="FAIL", done=true, info.fail=true
      (run_mypcbench.py step logging; env.py DONE/FAIL handlers)
    • PREDICT_CRASH: run_single_example except block writes
      action="PREDICT_CRASH", done=True   ← boolean True serializes as true
    │
    ▼
[B] paper2_exec_run.sh :: cell_has_done()
      grep -Eq '"action": "DONE"|"done": true' traj.jsonl
      ▲
      └── OR-alternative matches ANY episode-ending row with "done": true
          including FAIL and PREDICT_CRASH — not only action DONE
    │
    ▼
[C] After archive:
      if cell_has_done → write_leg_checkpoint(..., status="DONE", ...)
    │
    ▼
[D] write_leg_checkpoint sets has_done_action from the SAME regex:
      if grep -Eq '"action": "DONE"|"done": true' → done=true
      payload["has_done_action"] = (done == true)
      → false positives: has_done_action=true without action DONE
    │
    ▼
[E] CHECKPOINT.jsonl + paper2_leg_finished.json record status=DONE
```

### Code references (absolute)

1. **Traj crash writer** — `/mnt/data2/Vinh/agent/external/MyPCBench-main/agent-harness/run_mypcbench.py` · `run_single_example` predict `except` → `"action": "PREDICT_CRASH"`, `"done": True`.

2. **FAIL → done=true** — same file `env.step` path; `/mnt/data2/Vinh/agent/external/MyPCBench-main/agent-harness/env.py` · `step` for `FAIL` returns `done=True`.

3. **Misclassification** — `/mnt/data2/Vinh/agent/scripts/paper2_exec_run.sh`:
   - `cell_has_done` (≈ L163–167)
   - `write_leg_checkpoint` grep for `has_done_action` (≈ L217–219, L234)
   - post-leg branch `if cell_has_done … status DONE` (≈ L358–361)

4. **Same bug in resume helper** — `/mnt/data2/Vinh/agent/scripts/paper2_exec_resume_prep.sh` uses equivalent `re.search(r'"action": "DONE"|"done": true', …)`.

### What is *not* the culprit

- Vendored `parse_response` correctly maps `terminate/failure` → action `FAIL` and success → `DONE`.
- `result.txt` writing `1.0` means “react loop returned without raise,” **not** Paper-2 DONE status — separate channel (`run_mypcbench.py` comments ≈ L630–634).
- `has_done_action` is a Paper-2 shim field; it **amplifies** the bad grep rather than living inside the agent.

### Evidence snippet

`aggregation-f036/G0` last traj row:

```json
{"action": "PREDICT_CRASH", "done": true, ...}
```

Matching checkpoint:

```json
{"status": "DONE", "has_done_action": true, "task": "aggregation-f036", "leg": "G0", ...}
```

`grep '"action": "DONE"'` on that traj → **false**; `grep '"done": true'` → **true**.

Present at Flash start commit `68f30ea` (`git show 68f30ea:scripts/paper2_exec_run.sh` contains the same `grep -Eq '"action": "DONE"|"done": true'`).

---

## 4. Execution source inventory

SHA256 measured on node30 at investigation time. “Git tracked?” = present in `git ls-files` at HEAD `64054a1`.

| Layer | Absolute runtime path | SHA256 | Git tracked? | Git status / note | Role |
| --- | --- | --- | --- | --- | --- |
| Lane launcher | `/mnt/data2/Vinh/agent/scripts/paper2_exec_small_lane.sh` | `6fb25209065c19f71c8735c1a184ac5aea9f491e163c93c1ab62cb9774435e72` | yes | clean @ HEAD | SMALL key bind → `paper2_exec_run.sh` |
| Chain | `/mnt/data2/Vinh/agent/scripts/paper2_exec_small_9b_then_flash.sh` | `068ca329f0260db3e6d768807da10f4d8ff1a6f309a44d200588d526d82923fa` | yes | clean | 9B then Flash |
| Waiter | `/mnt/data2/Vinh/agent/scripts/paper2_exec_wait_9b_then_flash.sh` | `a1a97f7601084be3f86c8eecdec01321e3a5358624da73842b87ac8610b6781a` | yes | clean | poll → Flash |
| Paper-2 runner | `/mnt/data2/Vinh/agent/scripts/paper2_exec_run.sh` | `7676ad94c4270c0628e4f7b3d59b2c52d47995cdff8f8a4c6fe94167e519669f` | yes | clean @ HEAD (≠ Flash-start blob `346d66d9…` @ `68f30ea`) | legs, checkpoint, `cell_has_done` |
| Resume prep | `/mnt/data2/Vinh/agent/scripts/paper2_exec_resume_prep.sh` | `4fc07b27fc8f6c840454f2c8cd22d20dcce3af186ecd2f8ead27e2e988f6c67b` | yes | clean | backfill; **same DONE regex** |
| CF inject | `/mnt/data2/Vinh/agent/scripts/cf_inject.py` | `562a8be252c46a8c87bc803c157c18b81a0c86cd67829e335c37d7901add3d9c` | yes | clean | guest inject / probe |
| Cell order | `/mnt/data2/Vinh/agent/out/paper2_cell_order.json` | `9e77c0ff61c41dbb904d2063b449d2f54e893164e8da8a0fcc3c0e90b7bed667` | yes | clean | frozen schedule |
| Universe | `/mnt/data2/Vinh/agent/out/paper2_analysis_universe.json` | `c076e50d7681d07832076123e7c0cb57a14876e26a067bd2ccdfd701c1338a7c` | yes | clean | |M|,|T| |
| Manifest | `/mnt/data2/Vinh/agent/paper/paper2_counterfactual_eval/EXECUTION_MANIFEST.md` | `32c0a6a36644a8d3c4d7c39829a8ba2381ecd8c35ac455dead92b55e900b757a` | yes | clean | freeze policy |
| Agent loop | `/mnt/data2/Vinh/agent/external/MyPCBench-main/agent-harness/run_mypcbench.py` | `9792f0ae2c25ffcc5588af4190e3bdfcc414dcbe622d1c7b9c82db65d88a497a` | **NO** | gitignored `external/` | react loop, traj, result.txt |
| QEMU env | `/mnt/data2/Vinh/agent/external/MyPCBench-main/agent-harness/env.py` | `d05d278802d4e8343ce018f00457d3b1cfd3d1c75c00f2fe68dafee2266493e2` | **NO** | gitignored | QEMU, screenshot, step |
| Qwen shim | `/mnt/data2/Vinh/agent/external/MyPCBench-main/agent-harness/agents/qwen_cua.py` | `5a2bc727d5bcaa8e292f37630867b050485edce104df29a477d36330f2693c42` | **NO** | gitignored | `qwen_cuabash` |
| Vendored agent | `/mnt/data2/Vinh/agent/external/MyPCBench-main/agent-harness/agents/vendored_paper_results/qwen35vl_agent.py` | `f478ebe6cbdd54051d36d0e06814569ad33892dacd5710fc667a0e14e1f072c0` | **NO** | gitignored | prompt, parse, LLM |
| VL utils | `/mnt/data2/Vinh/agent/external/MyPCBench-main/agent-harness/agents/vendored_paper_results/utils/qwen_vl_utils.py` | `b8bf6e684dd3643743c8ff746ca1b552b6a1e0a66c3fff26e4f520c47ba091a0` | **NO** | gitignored | smart_resize |
| Prompts | `/mnt/data2/Vinh/agent/external/MyPCBench-main/agent-harness/agents/prompts.py` | `212b5310a782ef48fe97c7bb4884ffbf17d443880cc4385c2f0e1089e0c97621` | **NO** | gitignored | MYPCBENCH_CONTEXT |
| Base agent | `/mnt/data2/Vinh/agent/external/MyPCBench-main/agent-harness/agents/base.py` | `5b359b8acf26292b7df232994bab2889721e4444f1ee882decbca870ea664700` | **NO** | gitignored | encode_image etc. |
| Judge | `/mnt/data2/Vinh/agent/external/MyPCBench-main/agent-harness/judge_results.py` | `cd88a37c2b120572674115c8f4066dbb183a57e0c2aecf3ffa59c915f86ff429` | **NO** | gitignored | rubric post-step |

**Why gitignored:** `.gitignore` documents `external/` as “Upstream repo, fetched by scripts/setup_upstream.sh” — intended re-fetchable, but **Paper-2 measurement depended on this local tree** without a pinned commit/hash in git.

**Secrets:** `.env` under MyPCBench is gitignored (not listed; not hashed here).

**Non-execution dirty file:** `scripts/paper2_exec_large_lane.sh` modified locally — not on Qwen Flash path.

**Results:** `results/paper2_exec/qwen35-9b/` and `qwen38-flash/` are tracked as of `64054a1` (archived measurements). Live harness results under `external/MyPCBench-main/results/` may still exist as working copies from runs.

---

## 5. Reproducibility gaps and required remediation

| Gap | Why it matters | Minimal remediation (do **not** apply in Gate −1) |
| --- | --- | --- |
| Entire `external/MyPCBench-main/agent-harness/**` gitignored / untracked | Cannot reproduce Flash agent/env/parser from git alone; only on-disk SHA256 | Snapshot: pin SHA256 table (this manifest) + either (a) track a thin `vendor/mypcbench-harness@<tag>` subtree with the files above, or (b) record upstream git commit + verify script that fails if SHA256 drift |
| No nested `.git` in `external/MyPCBench-main` | Cannot `git describe` the harness | Prefer (a) or re-clone upstream at known commit and `sha256sum -c` against this inventory |
| `paper2_exec_run.sh` HEAD ≠ Flash-start blob | Current tree has GPT/OpenRouter guards post-Flash; Flash used `68f30ea` | For analysis cite `68f30ea:scripts/paper2_exec_run.sh`; for future Gate 0 freeze, tag a new commit after false-DONE fix |
| False-DONE regex in `cell_has_done` / `has_done_action` | Inflates DONE count (4 Flash legs) | Patch grep to **only** `"action": "DONE"` (and optionally last-row check); recompute CHECKPOINT offline; **do not** silently rewrite archived traj |
| Same regex in `paper2_exec_resume_prep.sh` | Resume/backfill can re-poison status | Same fix |
| `result.txt=1.0` ≠ Paper-2 DONE | Easy to confuse completion marker with success | Document in analysis; do not treat result.txt as DONE |
| Uncommitted `paper2_exec_large_lane.sh` | Noise / future Claude-GPT confusion | Commit or discard before LARGE work — out of Gate −1 scope |
| `GENERIC_AGENT_INVARIANTS.md` untracked | Docs only | Commit when authorized (not required to freeze past Flash) |

### Minimal remediation plan (ordered, future authorization only)

1. **Freeze harness hashes** from this inventory into `EXECUTION_MANIFEST.md` or a `HARNESS_PIN.json` (SHA256 list).  
2. **Fix** `cell_has_done` / `write_leg_checkpoint` / `resume_prep` to detect real DONE via `"action": "DONE"` only (last non-TOOL_CALL/EMPTY_XML row optional strengthening).  
3. **Offline reclassify** Flash CHECKPOINT (4 false-DONE → `TERMINAL_FAIL`, `has_done_action=false`) without re-running models.  
4. **Track or vendor** the small set of harness files in the inventory (or pin upstream commit + CI hash check).  
5. Only then authorize Gate 0 / generic-agent work against the frozen instrument.

---

## 7. Gate −1.5 addendum (2026-09-06)

Measurement remediation applied **without** re-running models:

- Tracked helper: `scripts/paper2_traj_terminal.py` — `VALID_DONE ⇔ last traj action == "DONE"`.
- Offline audit: `scripts/canonical_audit_paper2.py` → per-slug `CHECKPOINT.canonical.jsonl`.
- Patched: `scripts/paper2_exec_run.sh`, `scripts/paper2_exec_resume_prep.sh`.
- Pin file: `out/paper2_harness_pin.json`.

Historical `CHECKPOINT.jsonl` unchanged. Analysis freeze for Study 1 Qwen cells should cite canonical checkpoint + this gate.

**STOP after Gate −1.5 commit:** no Gate −2 / generic agent until independent review.

### Gate −1.5 closures (evidence completion)

| Closure | Artifact | Status |
| --- | --- | --- |
| A fail-closed matrix | `out/gate15_closure_A_matrix.md` | required before Gate −2 |
| B runtime/offline parity | `out/gate15_closure_B_parity.md` + `tests/test_paper2_terminal_parity.py` | mismatch blocks Gate −2 |
| C effective instrument pin | `out/paper2_harness_pin.json` + `out/gate15_closure_C_inventory.md` | pin-verify via `scripts/verify_paper2_harness_pin.py` |

Still **no Gate −2** until independent review of A/B/C.

---

## 8. Gate −2 open (protocol freeze) — 2026-09-06

Gate −1.5 **FINAL PASS**. Gate −2 artifact:

- `GENERIC_AGENT_PROTOCOL_SPEC.md` — extracted from pinned instrument; generic loop still **BLOCKED**.

Follow-ups (non-blocking):

1. Fallback-trap fixture `10_fallback_trap_done_then_malformed` (DONE@N−1 + malformed@N; no back-scan).
2. Vendor delta reviewability vs upstream = **optional**; SHA pin closes identity/drift (Gate −1 CLOSED).

