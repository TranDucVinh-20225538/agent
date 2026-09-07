# Study 2 Option L — cost / balance review (updated)

**Status:** REVIEW ONLY — does **not** modify preregistration · does **not** lock/sign · does **not** alter N/roster/protocol · no legs  
**Supersedes funding conclusion in:** `out/study2_option_L_cost_balance_review.md` §5–§6 (cost envelopes unchanged; **available balance corrected**)  
**Date:** 2026-09-06

---

## 1. Why the prior pull said ~$28 and you see ~$1.2k

Two **different** OpenRouter keys:

| Source | Key label (masked) | `limit` | `usage` | **`limit_remaining`** |
| --- | --- | ---: | ---: | ---: |
| Agent env pull `OPENROUTER_API_KEY_SMALL` @ 16:50Z (`GET /api/v1/key`) | `sk-or-v1-c86…537a` | $500 | ~$471.94 | **~$28.06** |
| Human-pasted `/api/v1/key` payload (this message) | `sk-or-v1-008…9dd` | $1500 | ~$231.51 | **~$1268.49** |

Prior review only saw **SMALL** in the agent environment (`OPENROUTER_API_KEY_LARGE` was **unset**). The ~$1.27k figure is real for the **other** key; it was not readable from this workspace’s env at pull time.

No full API secrets are stored in this artifact.

---

## 2. Cost requirement (unchanged accounting)

Same assumptions as `out/study2_cost_per_leg.md` / prior review: locked trio, Option L \(L=171\) (57×3), interactive list prices, low/mid/high token scenarios.

| Scenario | Est. total API $ for 171 legs |
| --- | ---: |
| low | ~$105 |
| mid | ~$348 |
| high | ~$982 |

---

## 3. Balance vs Option L (by funding lane)

### A. SMALL only (~$28.06)

| Scenario | Executable without more funding? |
| --- | --- |
| low / mid / high | **No** (shortfall ~$77 / ~$320 / ~$954) |

### B. Pasted key (~$1268.49 remaining)

| Scenario | Need | Remaining − need | Executable without additional funding? |
| --- | ---: | ---: | --- |
| low | ~$105 | ~+$1163 | **Yes** |
| mid | ~$348 | ~+$920 | **Yes** |
| high | ~$982 | ~+$287 | **Yes** (margin ~29% above high envelope) |

**Combined if both keys are usable for Study 2 legs:** remaining ≈ $28 + $1268 ≈ **$1296** (still **Yes** for low/mid/high under the same envelopes). Lane binding (which models may use which key) remains an **ops** constraint from the exec manifest — not re-decided here.

---

## 4. Updated executability verdict

On the **human-supplied key balance** (`limit_remaining` ≈ **$1268.49**):

**The full Option L matrix of 171 legs is financially executable without additional funding** under the project’s documented low/mid/**high** engineering envelopes (high still leaves ~$287 headroom before the key limit).

Caveats (ops, not N/method):

1. That funded key must actually be **bound** for GPT/Claude (and any allowed Flash) Study 2 traffic; SMALL alone still cannot carry the matrix.  
2. Envelopes are **not invoices**; a worse-than-high token path could still exhaust the key.  
3. This review does **not** sign Phase 4, lock N, or authorize legs.

---

## 5. Non-actions (confirmed)

- Preregistration not edited  
- No lock/sign  
- N / roster / protocol unchanged  
- No Study 2 matrix legs run
