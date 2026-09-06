# Gate 0A v1.1 cross-family summary

| Family | Candidate | P1 | P2 | P3 | P4 | DONE@ | Gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Qwen/Flash | `qwen/qwen3.8-flash` | ✓ | ✓ | ✓ | ✓ | 5/5 | **PASS** |
| GPT | `openai/gpt-5.5` | ✓ | ✓ | ✓ | ✓ | 2/2 | **PASS** |
| Claude | `anthropic/claude-opus-4.6` | ✓ | ✓ | ✓ | ✓ | 3/3 | **PASS** |

Protocol lock ancestry: freeze `dd43cbe` · Flash PASS then GPT/Claude on same v1.1 criteria (`max_steps=10`, token byte-exact + DONE).
No protocol/budget/instruction retune between families. Sequential runs; separate artifact/QEMU namespaces.

Roster decision: deferred to human (all three Gate 0A PASS → all qualified as Gate 0A candidates).
