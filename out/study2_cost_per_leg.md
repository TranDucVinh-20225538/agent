# Study 2 — cost-per-leg (OpenRouter) — planning only

**Status:** COST ENVELOPE ONLY — **not** a matrix lock; **not** a methodological N lock.  
**Pulled:** 2026-09-06 — OpenRouter list prices + SMALL key remaining magnitude.  
**Methodological N:** see `out/study2_phase4_preregistration_audit.md` (57/family is **conditional carry-forward**, not signed).

## Clarification (read first)

| Symbol | Meaning in *this* file |
| --- | --- |
| \(L_{full}\) = 171 = 57×3 | **Planning identity only:** IF Study 2 adopts Gate 0A roster \|M\|=3 AND the frozen analysis \|T\|=25 with \(n_{multiI}=7\), THEN legs = \(3\times25\times2+3\times7\). |
| 57 | Per-model leg count under that same IF — **Study 1 formula on frozen T**, not a new Study 2 sample. |
| Preregistered / locked matrix | **None yet.** Phase 4 lock block still has N **OPEN**. |

Do **not** read 171 as “the Study 2 matrix is locked.”

Valid methodological postures (human picks later; **no subsample seed chosen here**):

1. **Full analysis T** → planning \(L=171\) (57/model).  
2. **Subsample T** → \(L'\) only after a **seed-pre-registered** subsample amends Phase 4 (not done).  
3. **Defer** until budget lane exists.

Cost rows below are computed for posture (1) and for abstract per-leg rates usable once a locked \(L'\) exists.

---

## List prices (USD / 1M tokens)

| Model ID | Input | Output |
| --- | --- | --- |
| `qwen/qwen3.8-flash` | $0.15 | $0.47 |
| `openai/gpt-5.5` | $5.00 | $30.00 |
| `anthropic/claude-opus-4.6` | $5.00 | $25.00 |

Interactive (non-batch) assumed unless separately locked.

## Token/leg engineering scenarios

(Study 1 Flash traj sample n=20/57: median ~34 steps — **usage proxy only**, not invoice.)

| Scenario | steps | in_tok/turn | out_tok/turn |
| --- | --- | --- | --- |
| low | 20 | 8,000 | 200 |
| mid | 35 | 15,000 | 400 |
| high | 60 | 25,000 | 600 |

### USD / leg (model × scenario)

| Model | low | mid | high |
| --- | --- | --- | --- |
| Flash | ~$0.03 | ~$0.09 | ~$0.24 |
| GPT-5.5 | ~$0.92 | ~$3.05 | ~$8.58 |
| Claude Opus 4.6 | ~$0.90 | ~$2.98 | ~$8.40 |

### Cost if posture (1) planning identity \(L=171\) (57 legs × each of 3 models)

| Scenario | Est. total API $ |
| --- | --- |
| low | ~$105 |
| mid | ~$350 |
| high | ~$980 |

### Cost scale for a future locked \(L'\) (no seed chosen)

Per-model cost ≈ `(legs_per_model) × (USD/leg)`.  
For equal legs/model: `total ≈ L' × mean(USD/leg across 3 models)`.

| Scenario | ≈ USD per leg (mean of 3 models) | Example \(L'=57\) (1 model only) | Example \(L'=171\) |
| --- | --- | --- | --- |
| low | ~$0.62 | ~$35 | ~$105 |
| mid | ~$2.04 | ~$116 | ~$350 |
| high | ~$5.74 | ~$327 | ~$980 |

## SMALL lane reality

At pull: SMALL key remaining ≈ **$28** (limit ~$500 cumulative).  
Even mid-envelope **full planning 171** does not fit on current SMALL remaining for GPT+Claude. Funding/lane choice is **operational**, orthogonal to locking methodological N.

## What this file must not be used for

- Implying N=57 or L=171 is preregistered  
- Choosing a subsample seed  
- Starting Study 2 legs  
- Changing Gate 0A / roster / protocol
