# Preflight A — GPT Gate 0A P1 traj-echo / ownership provenance

**Mode:** evidence-only · **no** Study 2 matrix · **no** Gate 0A rerun · **no** protocol/roster/N/seed/config edits  

**Primary sources**

| Artifact | Path |
| --- | --- |
| Gate 0A GPT report | `results/paper2_exec/gate0a-gpt/gate0a_report.json` |
| Gate 0A GPT traj | `results/paper2_exec/gate0a-gpt/traj.jsonl` |
| Check definition | `scripts/paper2_gate0a_flash_smoke.py` |

Plaintext token appears in some cited lines below (already on disk in the report). Ownership conclusions use **sha256** equality.

**Planted / reported sha256 (equal):** `fafdef4c780b2f8d5b7e57044a911d02d35f9ad5d4f3e2714cf857111c96aaca`  
Evidence: report L10 `token_sha256` · L220 `agent_reported_token_sha256`.

---

## A1. Definition: traj-echo vs ownership path

| Term | Operational definition | Code / data |
| --- | --- | --- |
| **Traj-echo** | Planted token string appears in traj assistant `response` text (or report `response_has_token` / `prose_token_candidates`) | Traj schema writes `response` only — `traj.jsonl` L1–L2; check `p1_token_in_traj_after_client` at smoke L504–506 |
| **Client bash path** | Token in QEMU-executed bash result recorded as `bash_result_head` / extracted `agent_reported_token` | Report L45–46; extractors smoke L83–87, L486–488 |
| **Harness tool_response** | Token in *next-turn* user/instruction payload wrapped in `<tool_response>` | Report HTTP req#2 messages L156 |

`p1_token_in_traj_after_client` (report L19 = **false**) ≡ `_token_byteexact_in(traj_text, TOKEN) ∧ p1_token_via_client_bash` (smoke L505–506). It is **secondary**; PASS pillars use sha-match on bash-extracted token (smoke L556, L592 area).

---

## A2. Chronology with file:line evidence

### Before any model call — plant on QEMU

| Claim | Evidence |
| --- | --- |
| Plant path | report L204–207 `plant.path=/tmp/GATE0A_GPT_TOKEN.txt`, `output_has_token: true` |
| Check | report L16 `plant_token_on_qemu: true` |

### Turn 1 — model requests bash; client returns token; **no traj-echo**

| Claim | Evidence |
| --- | --- |
| Round | report L39 `"round": 1` |
| Assistant asks `cat` only (no token in prose) | report L40–41 `response_has_token: false`; traj L1 `action=TOOL_CALL`, response is bash XML only — **token not in traj line** |
| Client bash returns token | report L45–46 `bash_result_head` contains token · `bash_has_token: true` |
| First bash-with-token round | report L227 `first_bash_token_round: 1` |
| Provider completion lacks planted token | report L112 `response_contains_planted_token: false` · check L17 true |
| Turn-1 **request** messages lack **full** token | report L107 instruction has **prefix only** `Expected token prefix: GPTGATE0A-` (not the 16-hex body). Full body first appears at L156 (HTTP #2) |

### After turn-1 bash — token enters model-visible context via harness (not traj-echo)

| Claim | Evidence |
| --- | --- |
| HTTP #2 `n_messages: 4` | report L118 |
| Full token inside `<tool_response>…</tool_response>` in instruction | report L156 |
| Provider turn-2 completion still lacks planted token in response body flag | report L189 `response_contains_planted_token: false` |

### Turn 2 — DONE; **still no traj-echo**

| Claim | Evidence |
| --- | --- |
| Round | report L50 `"round": 2` |
| `response_has_token: false` | report L52 |
| `produced_done: true` / actions DONE | report L53–62 |
| Traj L2 | `action=DONE`, response is terminate XML only — **no token string in line** |
| `prose_token_candidates: []` | report L221 |
| `done_round: 2` | report L215 |

---

## A3. Answers (GPT-specific)

| # | Question | Answer | Exact support |
| --- | --- | --- | --- |
| 1 | What is traj-echo? | Token string in **traj assistant response**, not bash stdout / not harness `<tool_response>` | Def above; traj L1–L2; smoke L504–506 |
| 2 | Which turn? | **None** for GPT | L41, L52, L19, L221; traj L1–L2 |
| 3 | Real / hash / placeholder? | N/A for echo. Ownership token is **real plaintext** on bash path; sha matches planted | L45–46 real; L10==L220 |
| 4 | Before or after first bash? | N/A (no echo). First bash = turn 1 | L46, L227 |
| 5 | Full token in any model-visible context **before** first bash? | **No** | L112 false; L107 prefix-only; full token only L156 after bash |

---

## A4. Ownership provenance verdict (GPT)

**P1 ownership holds without traj-echo.**

Chain:

1. Plant only on QEMU (L16, L204–207)  
2. Turn-1 provider response does not contain planted token (L112, L17)  
3. Turn-1 model-visible instruction has prefix only, not full secret (L107)  
4. Client bash returns full token (L46, L18)  
5. Reported token sha == planted sha (L10, L219–220)  
6. Traj-echo absent (L19 false) is **instrumentation/behavior**, not pre-exec leakage  

**Classification:** GPT `p1_token_in_traj_after_client=false` ≠ P1 failure.
