# P3 — 20-cluster cohort feasibility (design only)

No trajectory. No agent run. No pre-registration of a comparative experiment
until this file’s gate is applied. Study 2’s 4-task support is not reused and
its statistic is not replaced.

Companion: `P3_COMPARATIVE_GATE.md` (n = task-clusters; threshold ≥ 20).

---

## 1. Task-cluster

One **cluster** = one task that, under a locked construct, has ≥ 2 models
assigned in advance. Raw model-pairs that share the task are one unit.
`n` = number of such tasks, not number of pairs, cells, or legs.

## 2. Inclusion / exclusion

**Include** a MyPCBench task only if all of:

* category ∈ {retrieval, aggregation, contradiction, counterfactual};
* gold is a path-lock into guest/probe state (Study 2 semantics), with ≥ 1
  determining component of kind `money_usd` | `integer` | `entity` |
  `categorical`;
* a G0/G1 intervention is specified (I1 sufficient);
* two models are named before any run on that task;
* the pair STS / Δ statistic is defined on that gold (same formula as Study 2
  `sts_leg` / pair mean).

**Exclude:** Study 2’s four C7 tasks (`counterfactual-f010`,
`preference_inference-f014`, `retrieval-f002`, `retrieval-f009`); the whole
sealed Paper 1 set; `situated_action`, `long_horizon`, `cua_only`, `hard_app`;
`preference_inference` (Study 2 already produced a vacuous path-null task in
this family); any task whose probe fails identifiability or whose gold is
null; `contradiction-f024` (already `REJECTED_CHANNEL_MISMATCH`).

## 3. Model set

The C7 pair, unchanged: **Flash** and **GPT** on the Study 2 generic-executor
protocol. A third model may be run; it does not increase `n`.

## 4. What stays frozen in the evaluator

Frozen: `extract_money` / `extract_int` / `extract_entity` / `extract_date`,
`_unique_or_none`, `match_one`, `sts_leg`, pair STS, ΔSTS = flash − gpt,
observation = last-response text, the P3-1 intervention family if the later
protocol uses it.

**Not** frozen onto new tasks: the Study 2 `LABELS` table (it has no keys
there). **Not** `R` (that is a different instrument; G2 closed). New tasks
require a **new label table**, authored and hashed **before** trajectory 1,
same authorship procedure as Study 2, no post-hoc edit. That is an extension
of inputs, not a new algorithm.

## 5. Gold construction

Per task, before any agent run: SQL/file probe → unique row → path lock →
kinds. `pending_probe` is not gold. Probe-only on the guest world is allowed
as **construction**, not as the comparative experiment. A cluster enters `n`
only after the lock exists and is non-null.

## 6. Minimum n

**n ≥ 20** task-clusters. Effect is not computed until this holds.

## 7. Independence

Clusters are independent units. Two pairs on one task = one cluster.
Oversampling candidates is required because probes fail: the candidate slate
below is 28; `n` is however many survive §5, and must be ≥ 20.

## 8. Lock-before-trajectory

Order, hard:

1. Freeze this file’s inclusion rule and the candidate slate.
2. Probe and lock gold on the slate (no agent).
3. If survivors < 20 → **stop** (§10). Do not add tasks after seeing which
   probes passed in order to chase 20. The slate is the slate.
4. Author and hash labels for survivors only.
5. Then, and only then, a comparative pre-registration may be written.
6. Then trajectories.

Step 3 is why the slate is 28, not 20: slack is declared now, not after
failures.

## 9. Power

n ≥ 20 is a **design gate for comparative scale**, not an 80% power
calculation. With 20 clusters, a rare flip remains a thin proportion. That
is accepted. We do not raise n after seeing a small effect. We do not hunt
flips.

## 10. Stop rule

If after step 3, n < 20: **NO**. Write path A. Do not lower 20. Do not fold
in the old 4. Do not add preference or sealed tasks. Do not start models.

---

## Candidate slate (28), mechanical

Pool = MyPCBench tasks in §2 categories, minus Study 2, minus sealed, minus
`contradiction-f024`, minus `preference_inference` (47 − 7 pref − 1 rejected
in-pool overlap = 40; `f024` is in the 47).

**First 12:** every remaining task that already has a Paper 2 intervention
row (`READY_RELATIVE` / `READY_FILE`, not rejected):

`aggregation-f004`, `aggregation-f036`, `aggregation-f040`,
`contradiction-f003`, `contradiction-f011`, `contradiction-f014`,
`contradiction-f017`, `contradiction-f022`, `counterfactual-f001`,
`counterfactual-f002`, `counterfactual-f003`, `retrieval-f005`.

**Next 16:** remaining pool IDs in lexicographic order:

`aggregation-f001`, `aggregation-f002`, `aggregation-f005`,
`aggregation-f008`, `aggregation-f009`, `aggregation-f010`,
`aggregation-f011`, `aggregation-f019`, `aggregation-f023`,
`aggregation-f029`, `aggregation-f030`, `aggregation-f031`,
`aggregation-f033`, `contradiction-f005`, `contradiction-f008`,
`contradiction-f012`.

This list is the feasibility object. It is not a result.

---

Probe protocol: `P3_COHORT_PROBE_PROTOCOL.md`. Both waves scored.

## Verdict (locked)

| Status | n |
|---|---|
| Wave A gold-locked | **9 / 12** |
| Wave B gold-locked | **7 / 16** |
| **n** | **16** |
| Threshold | 20 |
| Gate | **FAIL** |

**16 < 20.** Comparative branch closed for this archive/cohort. C7 is
existence only. Write path A. Do not lower 20. Do not rewrite D. Do not
fold in Study 2’s other eight. Do not start trajectories.
