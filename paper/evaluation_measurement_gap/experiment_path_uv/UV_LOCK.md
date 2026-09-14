# Path UV LOCK — CUAVerifierBench / Universal Verifier

**Status:** OPEN 2026-09-13. Parallel to Path B. Not Path A. Not M1a transport.

This is **our** instance of the UV architecture on a public screenshot
corpus. It does **not** audit Rosset’s published κ / FPR. Released
`uv_rubric_score` / `uv_outcome_success` are **not** gold and are **not** R.

## Question (two layers)

**U1 (machine, no LLM):** On released `trajectories`, how often
`n_screenshots > K`? That is a **necessary** condition for per-criterion
top-K to drop a frame. It is **not** the discard set.

True discard: a frame index that is in none of the per-criterion keep
lists after `[:K]` and the optional relevance filter. That requires
`step2_relevance_scores` (R). R is **not** in the public HF columns.

**U2 (human, after R exists):** Two stages (`CODEBOOK.md`). Isolation
DECISIVE is secondary. Primary = **IRRECOVERABLE** loss: discard frame is
isolation-DECISIVE **and** no keep-set frame is EQUIVALENT (stage 2).
REDUNDANT loss (equivalent evidence still kept) is reported separately.
It is not the M1a-shape analogue. Sample rule: `SAMPLE_LOCK.md` (frozen
before full 106-R). Forbidden gold: `uv_*`, `final_human_*`, LLM labels.

## Frozen constants (before U1 rates)

| Symbol | Value | Source |
|---|---|---|
| `K` = `max_images_per_criterion` | **5** | `MMRubricAgentConfig` default, `microsoft/fara` `mm_rubric_agent.py` |
| Sensitivity `K` | 3 and 7 | Pre-specified; do not pick after seeing U1 |
| Relevance filter | on (`ignore_irrelevant_screenshots=True`) | same config; only applied once R exists |
| Primary split | `fara7b_om2w_browserbase` (n=106, screenshots public) | CUAVerifierBench |
| Secondary split | `internal` (n=154) | same; report separately; do not pool |

Corpus: `microsoft/CUAVerifierBench` config `trajectories` (MIT).
UV source pin: fetch `webeval/src/webeval/rubric_agent/mm_rubric_agent.py`
from `microsoft/fara` `main` at fetch time; record sha256.

## Do not

- Use `uv_rubric_score` / `uv_outcome_success` as frame gold
- Use human outcome/process as frame gold
- Let an LLM (including this agent) substitute for U2 humans
- Call U1 “M1a transported” or E2
- Re-run UV until U1 is written and K stays frozen
- Reopen Path A; run extractor `3242c30`; retune K after rates
- Put U1 in `main.tex` as a second CORE
