# Study 2 — cost-per-leg (OpenRouter pull) → N options

**Status:** ESTIMATE — human must lock N / budget before matrix start.  
**Pulled:** 2026-09-06 via `GET https://openrouter.ai/api/v1/models` (list prices) + `GET /api/v1/key` (SMALL lane remaining).  
**No Study 2 legs run for this estimate.**

## List prices (USD / 1M tokens)

| Model ID | Input | Output |
| --- | --- | --- |
| `qwen/qwen3.8-flash` | $0.15 | $0.47 |
| `openai/gpt-5.5` | $5.00 | $30.00 |
| `anthropic/claude-opus-4.6` | $5.00 | $25.00 |

(Batch SKUs exist at ~½ price; Study 2 default assumes **interactive** non-batch unless separately locked.)

## Token/leg model (engineering scenarios)

Study 1 Flash traj sample (n=20/57): **median ~34 steps/leg**, mean ~36 (max 83).  
No per-leg OpenRouter usage fields in `CHECKPOINT*.jsonl` — costs below are **scenario envelopes**, not measured invoices.

Assume average request size grows with history+screenshots; scenarios multiply `(steps × in_tok/turn)` and `(steps × out_tok/turn)`:

| Scenario | steps | in_tok/turn | out_tok/turn |
| --- | --- | --- | --- |
| low | 20 | 8,000 | 200 |
| mid | 35 | 15,000 | 400 |
| high | 60 | 25,000 | 600 |

### Implied USD / leg

| Model | low | mid | high |
| --- | --- | --- | --- |
| Flash | ~$0.03 | ~$0.09 | ~$0.24 |
| GPT-5.5 | ~$0.92 | ~$3.05 | ~$8.58 |
| Claude Opus 4.6 | ~$0.90 | ~$2.98 | ~$8.40 |

Dominant cost: **GPT + Claude input** under long multimodal histories.

## Full-universe matrix (|M|=3, |T|=25, multiI=7)

\[
L = 3\times25\times2 + 3\times7 = 171 \text{ legs}
\]

(57 legs/model, same shape as Study 1 per-model count.)

| Scenario | Est. total API $ (equal mix) |
| --- | --- |
| low | ~$105 |
| mid | ~$350 |
| high | ~$980 |

## Lane reality check (SMALL key)

From OpenRouter `/api/v1/key` on `OPENROUTER_API_KEY_SMALL` (values not logged beyond magnitudes):

- Key **limit** ≈ $500 cumulative  
- **Remaining** ≈ **$28** at pull time  

Conclusion: **cannot** fund GPT+Claude Study 2 full 171-leg matrix on the current SMALL key alone. Options (human pick; do not silent-failover):

1. **Recharge / raise SMALL limit** to cover mid–high envelope + margin.  
2. **Dated operational amendment:** GPT/Claude Study 2 legs on `LARGE` / dedicated keys; Flash on SMALL — protocol unchanged.  
3. **Pre-registered \(\mathcal{T}\) subsample** (seed before any \(\tau\)) to cut \(L\) into budget — must amend Phase 4 lock block.  
4. **Defer** matrix until budget lane is explicit.

## Recommended decision inputs (for human)

| Question | Default proposal |
| --- | --- |
| Confirmatory \(\mathcal{T}\) | Full analysis 25 + 7 multi-I (no Gate 0A task) |
| \(\mathcal{M}\) | Gate 0A trio only |
| Planning scenario | **mid** (~$3/leg GPT/Claude; ~$350 total) + ≥30% contingency |
| N lock | Either **N=171** with funded lane, or seed-locked subsample with stated \(L'\) |

## What this gate does *not* do

- Does not change roster  
- Does not authorize matrix start  
- Does not retune Gate 0A  
- Does not treat estimates as invoices — after first ~5 Study 2 legs, reconcile measured OpenRouter generation cost and amend contingency only via dated note
