# Study 2 Round-57 preflight (launch plumbing)

**Verdict:** **PASS**
**Checked at (UTC):** 2026-09-06T17:37:00.397831+00:00

## A — Live balance (008…9dd)
- ok: `True`
- fingerprint: `sk-or-v1-008…9dd`
- limit_remaining: `1268.486531707`
- min_required_usd: `100.0`

## B — Shared executor evidence (not an approval gate)
- ok: `True`
- All Study 2 families use study2_run_mypcbench → qwen_cuabash + OpenRouterChatCompletionsTransport.

## C — Sealed universe / order vs locked manifest
- ok: `True`
- issues: `[]`
- prereg sha: `6803c6439af8ec579d6c74e3597bee5d3a3743bcd21b23b0145d7f4d33542a33`
- matrix: `{"T": 25, "n_multiI": 7, "N_fam": 57, "L_total": 171, "seed": 20260904, "first_task": "retrieval-f010", "first_legs": ["retrieval-f010:G0", "retrieval-f010:G1", "retrieval-f017:G0", "retrieval-f017:G1", "retrieval-f017:G2"]}`

JSON twin: `out/study2_round57_preflight.json`
