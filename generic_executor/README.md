# generic_executor (Phase 1)

**Freeze:** Gate −2 `GENERIC_AGENT_PROTOCOL_SPEC.md` (pin tip `a330e15`).

Behavioral protocol is **not** redesigned. This package:

1. Reuses frozen `QwenOSWorldAgent` (`enable_bash=True`) for prompt / XML parse / bash.
2. Runs a react loop mirroring `run_mypcbench.run_single_example`.
3. Classifies terminals with Gate −1.5 `paper2_traj_terminal`.
4. Plugs **transport only** via `FakeModel` (Phase 1 Commit A).

## Commit A — fake model (this)

```bash
python3 -m unittest tests.test_generic_executor_fake -v
```

Zero API, zero QEMU.

## Not yet

- Commit B: real transport adapters (Flash / OpenAI-compatible / Anthropic-compatible)
- Gate 0 / matrix / API spend
