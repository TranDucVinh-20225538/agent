# Prior-art matrix (markdown)

22 serious candidates, ranked roughly by similarity level (highest first). Machine-readable version: `03_prior_art_matrix.csv`. Full narrative on the top two: `08_direct_prior_art.md`.

| Paper | Year | Domain | Env. intervention | Paired runs | Tracking measured | Score sensitivity measured | Fixed rubric/judge | Type-B-like case | Level | Key difference |
|---|---|---|---|---|---|---|---|---|---|---|
| Turk — Counterfactual Evaluation... Clinical LLMs and Agents (2605.30590) | 2026 | Clinical LLM/agent decision support | Yes | Yes | Yes (CSS) | Partial | Yes | Yes | **2** | Different domain; CMS never recomputed on E1 per-instance |
| Dong et al. — How Benchmarks Mis-Score CUAs (2607.28367) | 2026 | Computer-use agents | No | No | Partial | No | Yes | No | **2** | Retrospective audit, not controlled intervention |
| Lù et al. — AgentRewardBench (2504.08942) | 2025 | Web agents | No | No | No | No | Yes | No | 2 | Judge-accuracy audit on fixed trajectories |
| Cao, Driouich, Thomas — Corrupt Success (2603.03116) | 2026 | Tool-use agents | No | No | Partial | No | Yes | Partial | 2 | Within-trajectory consistency, no re-run under intervention |
| Luo & Peng — AcquaBench (2607.24054) | 2026 | Web/retrieval agents | Partial | Yes | Yes | Yes | Yes | No | 2 | Manipulates info access, not world state; conflates GT and score |
| Zhou, Liu, Li, Rossi, Hu — Counterfactual Trace Auditing (2605.11946) | 2026 | Tool-use agents | Partial | Yes | Partial | Yes | Yes | Yes | 2 | Skill on/off, not environment state |
| Weng, Feng, Xie — Policy Invariance (2605.06161) | 2026 | LLM-as-judge (safety) | Partial | No | No | Yes | Yes | No | 2 | Perturbs judge policy text, no agent under test |
| Gao & Zhou — Evidence-Supported Bounds (2605.10448) | 2026 | Interactive agents | No | No | Partial | No | Yes | Partial | 1 | Post-hoc evidence audit |
| Advani — False Success (2606.09863) | 2026 | Tool-use agents | No | No | Partial | No | Yes | Yes | 1 | Retrospective classifier study |
| Gonzalez-Pumariega et al. — Reliability of CUAs (2604.17849) | 2026 | Computer-use agents | Yes (cosmetic) | Yes | No | Partial | Yes | No | 1 | Perturbs presentation, not task-relevant state |
| Sun et al. — AgentHijack (2605.25707) | 2026 | Computer-use agents | Yes | No | No | Partial | Yes | No | 1 | Perceptual/UI corruptions, no tracking axis |
| D'Oro et al. — Statistical Precipice (2605.08261) | 2026 | Computer-use agents | No | No | No | Partial | Yes | No | 1 | Statistics/memorization-gaming paper |
| Xue et al. — Online-Mind2Web / WebJudge (2504.01382) | 2025 | Web agents | No | No | No | No | Partial | No | 1 | Score-vs-reality divergence, no paired design |
| OSWorld (2404.07972) | 2024 | Computer-use agents | Partial | No | No | No | Yes | No | 1 | UI-clutter robustness sub-study only |
| AppWorld (2407.18901) | 2024 | Coding/tool agents | No | No | No | No | Yes | No | 1 | State-based scoring, no counterfactual intervention |
| GroundEval (2606.22737) | 2026 | Stateful agent eval | No | No | Partial | No | No | No | 1 | Deterministic judge replacement, no intervention |
| Bean et al. — Construct Validity (2511.04703) | 2025 | LLM benchmarks (445) | No | No | No | No | No | No | 1 | Observational survey |
| Hsia, Pruthi, Singh, Lipton — Goodhart / Explanation Benchmarks (2308.14272) | 2023 | NLP explanation metrics | Partial | No | No | Yes | Yes | Partial | 1 | Adversarial metric gaming, not GT state intervention |
| Chen, Cheung, Yiu — Metamorphic Testing (2002.12543) | 1998/2020 | Software testing | No | Yes | Yes (single layer) | No | No | No | 1 | MR is the sole oracle; no second held-fixed score |
| Ribeiro et al. — CheckList (ACL 2020) | 2020 | NLP model testing | No | Yes | Yes (single layer) | No | No | No | 0 | Input-text perturbation, single-layer check |
| Kaushik, Hovy, Lipton — Counterfactually-Augmented Data (1909.12434) | 2020 | NLP classification | No | Yes | Yes | No | No | No | 0 | Text-level editing, no environment state |
| Skalse et al. — Defining Reward Hacking (2209.13085) | 2022 | RL theory | No | No | No | No | No | No | 0-1 | Agent-side proxy exploitation, not evaluator-side |

**No candidate reaches Level 3.** Two candidates (Turk 2605.30590, Dong et al. 2607.28367) are the closest and are treated in depth in `08_direct_prior_art.md`.
