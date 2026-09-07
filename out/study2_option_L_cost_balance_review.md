# Study 2 Option L — cost / balance review (artifact only)

**Status:** REVIEW ONLY — does **not** modify preregistration · does **not** lock/sign · does **not** alter N/roster/protocol · no legs  
**Date (pull):** 2026-09-06T16:50:10Z  
**Matrix under review:** human-selected **Option L** fixed design — `|T|=25`, \(n_{\mathrm{multiI}}=7\), \(N_{\mathrm{fam}}=57\), \(|M|=3\), **\(L=171\)**  
**Accounting baseline:** same method as `out/study2_cost_per_leg.md` (OpenRouter interactive list prices × engineering token/leg scenarios)

---

## 1. Live billing/account pull

**Source:** OpenRouter `GET https://openrouter.ai/api/v1/key` (key-scoped limit / remaining).  
**Keys examined in env:** `OPENROUTER_API_KEY_SMALL` (present) · `OPENROUTER_API_KEY_LARGE` (**unset**) · unbound `OPENROUTER_API_KEY` / `OPENAI_API_KEY` (unset).  
**No secrets recorded in this artifact.**

| Key env | HTTP | `limit` (USD) | `usage` (USD) | **`limit_remaining` (USD)** | `limit_reset` |
| --- | ---: | ---: | ---: | ---: | --- |
| `OPENROUTER_API_KEY_SMALL` | 200 | 500.00 | 471.9434 | **28.0566** | null |
| `OPENROUTER_API_KEY_LARGE` | — | — | — | **unavailable (unset)** | — |

**Available OpenRouter funding in this environment (as pulled):** **≈ $28.06** on SMALL only. No LARGE key balance was readable because the LARGE env var is unset.

---

## 2. Live list prices (locked three candidates)

Pulled from OpenRouter `GET /api/v1/models` at the same timestamp; USD per 1M tokens:

| Model ID (roster) | Input / 1M | Output / 1M | vs `study2_cost_per_leg.md` |
| --- | ---: | ---: | --- |
| `qwen/qwen3.8-flash` | $0.15 | $0.47 | unchanged |
| `openai/gpt-5.5` | $5.00 | $30.00 | unchanged |
| `anthropic/claude-opus-4.6` | $5.00 | $25.00 | unchanged |

Interactive (non-batch) assumed, matching the project cost file.

---

## 3. Cost-accounting assumptions (unchanged)

From `out/study2_cost_per_leg.md` (usage **proxy**, not invoice):

| Scenario | steps/leg | in_tok/turn | out_tok/turn |
| --- | ---: | ---: | ---: |
| low | 20 | 8,000 | 200 |
| mid | 35 | 15,000 | 400 |
| high | 60 | 25,000 | 600 |

\[
\mathrm{USD/leg} = \mathrm{steps}\times\bigl(\tfrac{\mathrm{in}}{10^6}P_{\mathrm{in}}+\tfrac{\mathrm{out}}{10^6}P_{\mathrm{out}}\bigr)
\]

Option L schedule: **57 legs × each of 3 models** → **171** total API legs.

---

## 4. Updated cost range for Option L (\(L=171\))

### USD / leg (exact under §2–§3)

| Model | low | mid | high |
| --- | ---: | ---: | ---: |
| Flash | $0.0259 | $0.0853 | $0.2419 |
| GPT-5.5 | $0.9200 | $3.0450 | $8.5800 |
| Claude Opus 4.6 | $0.9000 | $2.9750 | $8.4000 |

### USD / family (57 legs)

| Model | low | mid | high |
| --- | ---: | ---: | ---: |
| Flash | $1.48 | $4.86 | $13.79 |
| GPT-5.5 | $52.44 | $173.57 | $489.06 |
| Claude Opus 4.6 | $51.30 | $169.58 | $478.80 |

### Full matrix total (171 legs)

| Scenario | Est. total API $ | ≈ mean $/leg |
| --- | ---: | ---: |
| **low** | **~$105.22** | ~$0.62 |
| **mid** | **~$348.00** | ~$2.04 |
| **high** | **~$981.65** | ~$5.74 |

(Rounded envelopes previously quoted as ~$105 / ~$350 / ~$980 remain valid; live prices did not move.)

---

## 5. Balance vs requirement

| Scenario | Estimated need | Available (`limit_remaining` SMALL) | Shortfall | Available / need |
| --- | ---: | ---: | ---: | ---: |
| low | ~$105.22 | ~$28.06 | ~$77 | ~27% |
| mid | ~$348.00 | ~$28.06 | ~$320 | ~8% |
| high | ~$981.65 | ~$28.06 | ~$954 | ~3% |

**GPT+Claude alone (114 legs), mid:** ~$343 ≫ $28.  
**Flash alone (57 legs), mid:** ~$4.86 — fits SMALL remaining, but is **not** the Option L full matrix.

---

## 6. Executability verdict

**The full Option L matrix of 171 legs is not financially executable on the currently available OpenRouter key balance without additional funding** (and/or provisioning a funded LARGE / alternate lane with sufficient remaining limit).

Even the **low** engineering envelope (~$105) exceeds SMALL remaining (~$28). Mid/high envelopes are far larger. `OPENROUTER_API_KEY_LARGE` is unset here, so no second OpenRouter balance offsets the gap in this pull.

This verdict is **operational / funding only**. It does not change Option L’s methodological N, the unsigned Phase 4 draft, roster, or protocol.

---

## 7. Non-actions (confirmed)

- Preregistration not edited  
- No lock/sign  
- N / roster / protocol unchanged  
- No Study 2 matrix legs run
