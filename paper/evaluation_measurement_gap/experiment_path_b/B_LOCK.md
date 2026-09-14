# Path B LOCK — WebJudge collect-then-filter

**Status:** B1 frozen 2026-09-13. B2 sample frozen; labels blocked.  
**Not Path A. Not M1a transport. Not E2 on `Score` as gold.**

## Question (two layers)

**B1 (machine, tonight):** Inside the released WebJudge o4-mini judge product, after
per-screenshot `Score` is collected, how often does `score >= T` enter the keep
list and then get dropped by `whole_content_img[:MAX_IMAGE]`?

That is instrument-internal post-collection discard of already-qualified frames.
It does **not** say those frames were determining for the task.

**B2 (human, blocked on screenshots):** Of frames in that discard set, which
does a human mark as decisive? Gold is human screenshot-grain labels.
Forbidden gold: `Score`, `final_eval`, task-level `human_label` alone.

## Frozen constants (before B1 rates)

| Symbol | Value | Source |
|---|---|---|
| `MAX_IMAGE` | 50 | `webjudge_online_mind2web.py` |
| Primary `T` | 3 | Xue et al. / WebJudge text: retain score ≥ 3 |
| Sensitivity `T` | 2 and 4 | Pre-specified; do not pick after seeing B1 |
| Judge product | `webjudge_o4-mini/*.json` | Official released o4-mini |

Keep-list reconstruction (locked): walk `image_judge_record` in released order;
a frame is **QUALIFIED** iff `Score >= T`; QUALIFIED frames in order form `R`;
`A(R) = R[:50]`; **DISCARD** = `R[50:]`.

Score `< T` is **not** M1a-shape. It is threshold exclusion (never entered `R`).

## Do not

- Use `Score` as determining gold
- Use `final_eval` or task `human_label` as frame gold
- Let an LLM (including this agent) substitute for B2 humans
- Reopen Path A
- Run extractor `3242c30`
- Retune `T` or `MAX_IMAGE` after seeing discard rates
- Claim public CUA benches are invalid
