# Gate 0A — P1 sha-match consistency audit

**Status:** PASS  
**Scope:** Flash / GPT / Claude Gate 0A v1.1 reports only (no retest).  
**Question:** Do GPT and Claude have the same *primary* ownership evidence strength as Flash?

## Primary evidence (required; same strength)

For each family, PASS requires all of:

| Check | Meaning |
| --- | --- |
| `plant_token_on_qemu` | Token exists only after QEMU plant |
| turn-1 provider response lacks planted token | No pre-exec provider leakage |
| `p1_token_via_client_bash` | Client-owned bash returned the token |
| `agent_reported_token_sha256 == token_sha256` | Byte-exact / sha-match content correctness |
| `p4_token_byteexact` + `p4_token_via_client_bash_byteexact` | Same value on tool path |
| turn-1 `has_tools=false` | Stateless prompt/XML path (P3 overlap) |

### Results

| Family | Model | sha-match | plant | no t1 leak | client bash | byteexact | t1 tools |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Flash | `qwen/qwen3.8-flash` | ✓ | ✓ | ✓ | ✓ | ✓ | false |
| GPT | `openai/gpt-5.5` | ✓ | ✓ | ✓ | ✓ | ✓ | false |
| Claude | `anthropic/claude-opus-4.6` | ✓ | ✓ | ✓ | ✓ | ✓ | false |

**Verdict:** Primary P1 + content sha-match evidence is **uniform across families**. GPT/Claude are not weaker than Flash on the decision-critical ownership chain.

## Secondary / instrumentation note (not a Gate fail)

| Family | `p1_token_in_traj_after_client` | Note |
| --- | --- | --- |
| Flash | true (in report) | v1.1 `traj.jsonl` not retained in `gate0a-flash/` (report+nohup only); v1.0 archive has traj |
| GPT | **false** | Traj stores assistant `response` + env `action`, **not** bash stdout. GPT did not echo the token in assistant prose before DONE, so traj lacks the string even though client bash + report sha-match hold |
| Claude | true | Assistant prose quoted the token on the DONE turn → traj contains reported token |

Interpretation: the GPT secondary flag is an **artifact-schema / echo** asymmetry, not missing ownership. Gate decisions use **sha-match of `agent_reported_token` extracted from client bash**, which is present and equal for all three.

## Decision

- Consistency audit: **PASS**
- No Gate 0A retest required
- Optional later hardening (not blocking): persist `bash_result` into traj lines for audit convenience
