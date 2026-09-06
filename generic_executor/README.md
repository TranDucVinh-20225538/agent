# generic_executor (Phase 1)

**Freeze:** Gate −2 `GENERIC_AGENT_PROTOCOL_SPEC.md` (pin tip `a330e15`).

Behavioral protocol is **not** redesigned. This package:

1. Reuses frozen `QwenOSWorldAgent` (`enable_bash=True`) for prompt / XML parse / bash.
2. Runs a react loop mirroring `run_mypcbench.run_single_example`.
3. Classifies terminals with Gate −1.5 `paper2_traj_terminal`.
4. Plugs **transport only** via `Transport` (`complete(messages) → text`).

## Commit A — fake model

```bash
python3 -m unittest tests.test_generic_executor_fake -v
```

## Commit B — OpenRouter chat-completions (mock HTTP)

```bash
python3 -m unittest tests.test_openrouter_transport -v
```

- `transport.py` — `Transport` + `install_transport` / system addenda
- `openrouter_chat.py` — stateless `/chat/completions` (no `previous_response_id`, no `tools`)
- `family_config.py` — Flash / Qwen9B / GPT-family / Claude-family request shaping

Live API / Gate 0 / QEMU / matrix: **not** authorized in Phase 1B.

## Not yet

- Gate 0 Flash / GPT-family / Claude-family
- Matrix / API spend
