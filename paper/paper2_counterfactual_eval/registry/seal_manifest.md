# Paper 2 seal manifest

Generated: 2026-09-03T19:14:00Z UTC
Spec: `paper/paper2_counterfactual_eval/PAPER2_SPEC.md`
Multi-I seed: `20260903` (not `20260826`)

## Sealed models (§3)

**4 models** — satisfies minimum ≥4 CUAs, ≥2 providers, ≥1 open-weight.

| id | agent_type | provider |
| --- | --- | --- |
| `claude-opus-4-6` | `claude_cuabash` | anthropic |
| `gpt-5.5` | `openai_cuabash` | openai |
| `qwen/qwen3.8-flash` | `qwen_cuabash` | openrouter |
| `qwen/qwen3.5-9b` | `qwen_cuabash` | openrouter |

Qwen 9B added as 4th model so Layer B retains ≥3 ranked agents if one model falls below `n_min=3` valid pairs. Qwen3.5-35B-A3B replaced by Qwen3.8-Flash per the `PAPER2_SPEC.md` §3 amendment log (2026-09-03) — execution feasibility/budget, before any Paper 2 execution, not a Paper 2 outcome (see PAPER2_SPEC.md §3 for the full amendment text).

## Sealed task universe (§4)

**27 tasks** — all eligible under Paper 2 §4 (no channel_invariant).
Paper 1 ten excluded via `cf/phase_b_registry.json`.

### Exclusion funnel (not mutually exclusive)

| reason | n |
| --- | ---: |
| `not_dv_from_answer` | 145 |
| `cua_required` | 128 |
| `gui_artifact` | 71 |
| `no_mapped_sqlite` | 23 |
| `in_paper1_ten` | 10 |
| `instruction_pins_gold` | 1 |

- Eligible: **27** / 184 screened

### By category

| category | n |
| --- | ---: |
| aggregation | 5 |
| contradiction | 8 |
| counterfactual | 6 |
| preference_inference | 2 |
| retrieval | 5 |
| situated_action | 1 |

### By state family (pre-run tags)

| state_family | n |
| --- | ---: |
| aggregation | 5 |
| categorical | 1 |
| numeric | 5 |
| preference_recommendation | 2 |
| relational_joint | 9 |
| temporal | 5 |

## Multi-I subset (§4 robustness)

**7 tasks** get an extra G₂ leg (min(8, ⌈0.25×27⌉) = 7):

- `aggregation-f040`
- `contradiction-f006`
- `contradiction-f011`
- `counterfactual-f002`
- `counterfactual-f003`
- `preference_inference-f014`
- `retrieval-f017`

## Leg count (§ Cost)

- Base paired legs: |M| × |T| × 2 = 4 × 27 × 2 = **216**
- Multi-I extra: |M| × 7 = 4 × 7 = **28**
- **Total ≈ 244 legs**

### Wall-time estimate (planning only)

Sources (TCG, no KVM — same harness as Paper 1):

- Floor **~12 min/leg**: `results/counterfactual_report.md` (retrieval-f001 base + CF harness wall, Aug 2026).
- Ceiling **~32 min/leg**: Round 24 mixed Paper 1 universe (internal run log; aggregation/contradiction tasks run longer).

Planning range **12–32 min/leg** → **~48–130 hours** serial wall time (244 legs). Parallelism depends on host/QEMU slots.

## Next (PAPER2_SPEC)

1. ~~Agree spec~~ · ~~Seal lists~~ (this file)
2. Registry rows: D, kind, role, wᵢ per task (before inject-probe)
3. Inject-probe identifiability on sealed universe
4. Agent runs (no ID changes after outcomes)

