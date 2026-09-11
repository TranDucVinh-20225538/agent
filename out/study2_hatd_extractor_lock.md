# Study 2 hat-D extractor lock

Frozen **before** STS aggregates. Matching stays in `protocol/matching.py` (untouched).

## Source

Last well-formed `traj.jsonl` row, field `response`. Strip `<think>…</think>`. If that row’s action is `DONE`, that response is the candidate answer. Intermediate step chatter is not used.

## Gold (separate reader)

`out/study2_gold_path_lock.json`. Per-leg `*.guest.json`. Injected legs use `probe_after` / `extra_probes_after`. Never the other leg. Never writer `track`.

## Fail-closed

Missing, unparseable, or two conflicting parsed values for one component → `None`. `matching.py` treats `None` as mismatch. Do not pick the gold-matching candidate.

## No LLM

Regex / labeled-field parsers in `scripts/study2_hatd_extract.py`, keyed by `(task, component_id)` plus `kind`. No paraphrase table.

## Kinds

| kind | extract |
|---|---|
| money_usd | first labeled `$` / numeric after the label; ignore a following Breakdown block |
| integer | first labeled int |
| entity / categorical | confirmation `AA-123`, email, or next non-junk line; dates `YYYY-MM-DD` when `component_id` contains `date` |
| state (`oddsmarket_gme_yes`) | `{shares: int, status: active\|settled}` |

## Tests

`tests/test_study2_hatd_extract.py` — hand-written fixtures only (no live 34-leg dumps).
