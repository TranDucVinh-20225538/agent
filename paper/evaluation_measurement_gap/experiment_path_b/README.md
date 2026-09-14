# Path B — WebJudge collect-then-filter

See `B_LOCK.md`, `RESULT.md`.

| Layer | Status |
|---|---|
| B1 machine discard after `Score≥T` then `[:50]` | **DONE.** 10/1790 cap-hits at T=3, all Operator. |
| B2 human decisive-frame | **Sample frozen** (30 episodes, 1065 items). **Blocked** on screenshots. |

`Score` is never gold. This agent is not a B2 annotator.

```bash
python3 experiment_path_b/fetch_webjudge.py
python3 experiment_path_b/classify_b1.py
python3 experiment_path_b/sample_b2.py
```

Request screenshots: `AUTHOR_REQUEST.md`.
