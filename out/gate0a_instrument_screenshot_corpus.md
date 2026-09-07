# Gate 0A Flash — screenshot action corpus check

Before adding `screenshot` as a recognized no-op, counted
`<parameter=action>screenshot</parameter>` across parsed `traj.jsonl` under
`results/` (JSON-decoded responses).

| Scope | Matches | Files |
|-------|---------|-------|
| All `results/**/traj.jsonl` | **22** | **18** |
| `study2-flash` | 6 | 5 |
| Study 1 `qwen38-flash` (+ related) | remainder | — |

**Verdict:** recurring protocol/output artifact (not a one-off). Instrument maps
screenshot-only turns → `WAIT` no-op via `apply_screenshot_noop` (does not
replace non-empty action lists, so a click+screenshot turn keeps the click).
