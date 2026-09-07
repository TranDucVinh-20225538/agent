# Gate 0A — P1 traj-echo evidence addendum

**Status:** evidence-only (no Gate 0A rerun; no protocol/roster change)  
**Companion to:** `out/gate0a_p1_consistency_audit.md`  
**Sources:** `results/paper2_exec/gate0a-{gpt,claude,flash}/gate0a_report.json` (+ `traj.jsonl` where present)

Tokens below are referred to by **sha256 only** (no plaintext reprint).

---

## 1. What is traj-echo?

**Definition (this audit):** appearance of the **planted token string** inside the
**assistant `response` field written to `traj.jsonl`** (and equivalently in
`response_head` / `prose_token_candidates` in the Gate 0A report).

It is **not**:

- bash stdout / `bash_result_head` (that is the **client tool path**),
- `<tool_response>…</tool_response>` text the harness injects into the *next*
  turn’s user/instruction payload (that is **client-owned observation**),
- the instruction line `Expected token prefix: …GATE0A-` (prefix only).

`p1_token_in_traj_after_client` is true iff the **reported token string** appears
somewhere in traj text after client bash succeeded.

---

## 2–4. Per-family evidence table

| Family | Traj on disk | Traj-echo? | Turn of echo | Echo content | Before/after first bash? |
| --- | --- | --- | --- | --- | --- |
| **GPT** | yes (2 lines) | **No** | — | — | First bash = turn **1** (`bash_has_token=true`). No assistant prose ever contains the token (turns 1–2 `response_has_token=false`; `prose_token_candidates=[]`) |
| **Claude** | yes (3 lines) | **Yes** | traj **step 3** / report turn **3** (DONE) | **Full real token** — sha256 `5b978aba…a70d1c72` equals planted sha; **not** a hash/placeholder | **After** first bash (bash token round **1**). Turn 3 response quotes prior `<tool_response>` then terminates |
| **Flash** | **no** v1.1 traj retained (report only) | Report: turn **5** `response_has_token=true`; `prose_token_candidates` len=1 with sha=`5b50fd3f…4643293f` = planted | turn **5** (DONE) | Full real token (sha-match); not placeholder | **After** first bash (round **1**) |

### Claude echo context (redacted)

Traj step 3 / DONE response contains a fenced copy of the token after prose
claiming it came from a prior `tool_response` (substring pattern:
`prior tool_response:` + fence + `[TOKEN]` + `I have confirmed the token via the`).

### GPT traj steps (no echo)

| step | action | `resp_has_reported` |
| --- | --- | --- |
| 1 | `TOOL_CALL` | false |
| 2 | `DONE` | false |

---

## 5. Any model-visible full token **before** first bash?

**No** for all three families, on the evidence below.

### 5.1 Turn-1 provider completion

| Family | `http_requests[0].response_contains_planted_token` |
| --- | --- |
| GPT | **false** |
| Claude | **false** |
| Flash | **false** |

### 5.2 Turn-1 request messages (model-visible context before any client bash result)

| Family | Full reported token in `messages_redacted`? | What *is* present |
| --- | --- | --- |
| GPT | **false** | Prefix only: `Expected token prefix: GPTGATE0A-` (instruction template) |
| Claude | **false** | Prefix only: `Expected token prefix: CLAUDEGATE0A-` |
| Flash | **false** | Prefix only: `Expected token prefix: FLASHGATE0A-` |

Note: turn-1 redacted blob also contains the **literal words** `<tool_response>`
because the *task instruction* mentions that tag — that is **not** a filled
tool result and does **not** contain the secret token body.

### 5.3 When the full token first enters model-visible messages

For all three: **HTTP request #2** (`n_messages` 4), inside harness-injected
`<tool_response>[TOKEN]</tool_response>` — i.e. **after** turn-1 client bash.

---

## Primary P1 verdict (evidence-backed)

P1 ownership + content correctness does **not** require traj-echo.

| Required primary check | GPT | Claude | Flash |
| --- | --- | --- | --- |
| `plant_token_on_qemu` | true | true | true |
| t1 provider lacks planted token | true | true | true |
| Full token absent from t1 messages | true | true | true |
| `p1_token_via_client_bash` / bash_has_token @ round 1 | true | true | true |
| `agent_reported_token_sha256 == token_sha256` | true (`fafdef4c…c96aaca`) | true (`5b978aba…a70d1c72`) | true (`5b50fd3f…4643293f`) |
| `p4_token_byteexact` + client bash byteexact | true | true | true |

**Verdict:** Primary P1 is **PASS with equal strength** across GPT/Claude/Flash.
Traj-echo is a **secondary instrumentation/behavior difference** (Claude/Flash
prose-quote on DONE; GPT does not). GPT’s `p1_token_in_traj_after_client=false`
is explained by (a) traj schema omitting bash stdout and (b) no assistant echo —
**not** by pre-bash leakage or missing client token.

No Gate 0A retest indicated.
