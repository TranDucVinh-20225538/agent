# Study 2 matrix — dry validation report (inspect-only)

**Verdict:** **PASS**  
**Checked at (UTC):** 2026-09-06T17:23:46.004675Z  
**JSON twin:** `out/study2_matrix_dry_validation.json`  
**Matrix launched:** **no**

---

## Binding

| Field | Value |
| --- | --- |
| Fingerprint | `sk-or-v1-008…9dd` |
| Source slot (pre-bind) | `OPENROUTER_API_KEY_LARGE` |
| Base URL | `https://openrouter.ai/api/v1` |
| SMALL / Gate0A / Anthropic | unset after bind |

---

## Generic OpenRouter path resolution

| Order | Family | Model ID | Out dir | Transport |
| ---: | --- | --- | --- | --- |
| 1 | flash | `qwen/qwen3.8-flash` | `results/paper2_exec/study2-flash` | `OpenRouterChatCompletionsTransport` |
| 2 | gpt | `openai/gpt-5.5` | `results/paper2_exec/study2-gpt` | same |
| 3 | claude | `anthropic/claude-opus-4.6` | `results/paper2_exec/study2-claude` | same |

Agent: frozen `qwen_cuabash` via `build_qwen_cuabash_agent` + `install_transport` (not native Claude/GPT agents; not Gate 0A smoke).

---

## Planned legs

| Quantity | Count |
| --- | ---: |
| Per family | 57 |
| Families | 3 |
| **Total** | **171** |
| G2 (multi-I) per family | 7 |

First units: `retrieval-f010` G0→G1, then `retrieval-f017` G0→G1→G2.

---

## Entrypoint hygiene

Scanned Study 2 scripts: no Gate 0A smoke launcher, no `paper2_exec_small_lane`, no `paper2_exec_large_lane` as launch path. SMALL appears only in forbid/scrub guards.
