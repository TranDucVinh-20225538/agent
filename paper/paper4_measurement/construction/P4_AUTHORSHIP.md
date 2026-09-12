# P4 independent V authorship (construction safeguard)

**Status: locked before any last-response exists.** $0. No instrument.
No scoring of `V*`. No leftover listing. No agents.

This file is the safeguard named in `P4_PREREG.md` §4.2. It is not an
implementation of the §2 instrument.

## Why

A single operator who writes Q and then “the same thing with new numbers”
for V makes held-out a copy of qualification. P4 forbids that. V last-
responses must be produced by a frozen generator from a disjoint parameter
table, not by restyling Q.

## Roles

| Role | Author | Inputs | Outputs |
|---|---|---|---|
| Q | operator, Q word-list only | `params_q.json` | `slate/q/*.json` |
| V | generator (this package) | `params_v.json` | `sealed/v/*.json` |
| R | generator | `params_r.json` | `slate/r/*.json` |

The generator is `generate_slate.py`. It has no `if cluster_id == …`
branch. Markup dialect for V is `['tool','unterminated','sandbox'][(n-1)%3]`
on the numeric suffix. Kind and gold come from the param row.

## Disjoint cover tokens

`wordlists_q.txt`, `wordlists_v.txt`, `wordlists_r.txt` are pairwise
disjoint. A Q instruction or observation may not contain a V or R cover
token as a whole word; symmetrically for V and R. Shared English
(`the`, `is`, `report`) is allowed.

## What may be hand-written

Parameter rows: instruction, anchors, component_id, kind, gold, wrong,
c5_distractor, c6_distractor, other_kind_token. Not last-responses.

## What may not

- Hand-editing generated `observations.*` on V or R.
- Copying a Q last-response into V with substitutions.
- Putting expected `{status, cause, committed}` on V files.
- Running §2 as a scorer on `V*` (construction audit computes spec-traces
  for **Q only**).

## Seal

After generation and mechanical audit PASS, `seal_v.py` hashes canonical
JSON of `V01`–`V20` and records `generator_sha256`, `params_v_sha256`,
`wordlist_v_sha256`. Scoring `V*` before freeze voids the seal.
