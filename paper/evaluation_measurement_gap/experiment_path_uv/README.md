# Path UV — CUAVerifierBench / Universal Verifier

See `UV_LOCK.md`. Parallel to Path B. Screenshots are public; R is not.

| Layer | Status |
|---|---|
| U1 `n_screenshots > K` | runnable after `fetch_uv.py` |
| Recover R (re-run UV) | blocked on API — `U_RERUN.md` |
| U2 human decisive-frame | blocked on R |

```bash
python3 experiment_path_uv/fetch_uv.py
python3 experiment_path_uv/classify_u1.py
```
