# Paper 2 — errata record

**This file records. It does not correct.** No frozen artifact is modified: `main.tex`,
`main.pdf`, `checklist.tex`, `table_primary.tex`, the figures, `out/study2_*`, the gold
lock, the extractor at `3242c30`, and every archive are untouched. The submitted state
remains reachable at tag `paper2-frozen`.

| id | date | severity | affects a published conclusion? |
|---|---|---|---|
| E-1 | 2026-09-12 | minor | no |

---

## E-1 — Unresolvable gold is scored as a mismatch, and the aggregate does not carry the flag

### What the instrument does

`out/study2_gold_path_lock.json` deliberately records **no gold formula** for either
component of `preference_inference-f010`:

```json
"preference_inference-f010": {
  "fastest_sender":              {"kind": "entity",  "path": null,
                                  "note": "no frozen formula on timestamp lists"},
  "designated_sender_latency":   {"kind": "integer", "path": null,
                                  "note": "no frozen latency formula"}
}
```

So `gold_for_component` returns `None` for both components on every leg of that task, on
every lane. Three frozen functions then convert "no formula exists" into "the agent was
wrong":

* `study2_hatd_apply.match_one` opens with `if gold is None or reported is None: return
  False`, so an unresolvable component is a **mismatch**, not an abstention;
* `protocol/matching.sts_leg` sums `den` over every component of positive weight,
  including the unresolvable ones, so the vacuous pair yields `0/2 = 0.000` rather than
  an undefined value;
* `protocol/matching.binary_track` requires a match on both legs, so it yields `Y=0`.

In $\mathcal{A}$ this binds on exactly one pair, `flash/preference_inference-f010`, whose
two legs are the only vacuous-gold legs among the 36. Verified from
`out/study2_hatd_legs.jsonl`:

```
flash/preference_inference-f010/G0  gold={'fastest_sender': None, 'designated_sender_latency': None}
                                    matches={'fastest_sender': False, 'designated_sender_latency': False}
                                    sts_leg=0.0
flash/preference_inference-f010/G1  (identical)
```

### What was disclosed, and what was not

The row-level fact **was** disclosed. `out/study2_sts_pairs.md` carries a dedicated
`gold_null` column with `True` on that row, and states in its header:

> `preference_inference-f010` gold=null (no frozen latency formula) → fail-closed match 0

This is therefore **not an undisclosed computational error.** It is a documented
fail-closed convention.

What was not carried is the flag at the point of aggregation. The same artifact ends
with

```
- Flash mean pair-STS=0.22916666666666666 mean Y=0.0 n=8
```

which pools the vacuous pair into the denominator with no indication that one of the
eight was never evaluable, and it is this aggregate that propagated into the submitted
paper. A reader of `main.tex` sees `n=8` and `0.229` with no way to know that one pair
carries no resolvable gold.

Separately, the convention conflicts with the vacuity principle adopted later in the
Paper 3 pre-registration — *unkeyed or unresolvable is vacuous, never a mismatch*
(`P3_0_SPEC.md` §2, restated in `P3_0_RECALL_AUDIT_SPEC.md` §4.1). Paper 2 and Paper 3
should not disagree about this silently.

### Affected published statements

All in `paper/paper2_eiaw_submission/main.tex`.

| loc | as submitted | on the 7 evaluable pairs |
|---|---|---|
| Table 1 `tab:coverage`, Flash row | `8` and `0.229` | $\vert\mathcal{A}\vert=8$ unchanged as a **coverage** count; mean STS `0.262` on $n=7$ |
| §4, "mean $\mathrm{STS}$ on $\mathcal{A}$ is $0.130$, $0.229$, and $0$" | `0.229` | `0.262` |
| §5, "on each agent's own $\mathcal{A}$, Flash is higher on \emph{both} layers ($\mathrm{STS}$ $0.229$ versus $0.130$)" | `0.229` versus `0.130` | `0.262` versus `0.130`; **direction unchanged and strengthened** |
| §4, "$Y=0$ on all $18$ valid pairs across all three agents" | `18` | $Y=0$ on the **17 evaluable** pairs; 1 pair is not evaluable |

GPT-5.5 (`0.130`, $n=9$) and Claude (`0`, $n=1$) are unaffected: neither has
`preference_inference-f010` in its $\mathcal{A}$.

Reproduction:

```
python3 - <<'PY'
import json
rows=[json.loads(l) for l in open('out/study2_hatd_legs.jsonl') if l.strip()]
def mean(lane, drop):
    p={}
    for r in rows:
        if r['lane']!=lane: continue
        if drop and all(v is None for v in r['gold'].values()): continue
        p.setdefault(r['task'],[]).append(r['sts_leg'])
    f={t:v for t,v in p.items() if len(v)==2}
    return len(f), sum(sum(v)/2 for v in f.values())/len(f)
print('flash kept   ', mean('flash', False))   # (8, 0.2292)
print('flash dropped', mean('flash', True))    # (7, 0.2619)
PY
```

### Not affected

The $\arg\max$ analysis of §5 is untouched, because `preference_inference-f010` is **not
in the common support**. $\mathcal{A}^{\cap}$ is
$\{$`counterfactual-f010`, `preference_inference-f014`, `retrieval-f002`,
`retrieval-f009`$\}$ — GPT-5.5 has no valid pair on `preference_inference-f010`, so the
task cannot enter the intersection. Therefore these all stand exactly as published:

* mean $S^0$ on $\mathcal{A}^{\cap}$: $49.5$ GPT versus $96.0$ Flash, Flash$-$GPT
  $=+46.5$, 95% CI $[21.0,\,72.0]$;
* mean STS on $\mathcal{A}^{\cap}$: $0.250$ GPT versus $0.208$ Flash, Flash$-$GPT
  $=-0.042$, 95% CI $[-0.125,\,0.000]$;
* $\arg\max S^0 =$ Flash, $\arg\max \mathrm{STS} =$ GPT-5.5, and the $\arg\max$ flip
  resting entirely on `retrieval-f009`;
* the $69.3\to49.5$ versus $95.8\to96.0$ common-support asymmetry;
* the STS granularity $\{0.000,\,0.333,\,0.500\}$ remark;
* coverage: DONE $32/29/4$ of $57$, $\vert\mathcal{A}\vert = 9/8/1$, since these are
  statements about **canonical termination** and do not depend on gold resolvability;
* Layer A's degeneracy conclusion. There is still no positive class: $Y=0$ holds on all
  17 evaluable pairs, so $S^0$ still cannot separate $Y=1$ from $Y=0$.

### Assessment

No published conclusion changes. The single affected comparison — Flash higher than
GPT-5.5 on both layers on each agent's own $\mathcal{A}$ — keeps its direction and
widens, so the correction cannot be said to favour the paper's narrative by removing an
inconvenient pair; it removes a pair that was depressing Flash.

The substantive lesson is about reporting rather than about arithmetic: a fail-closed
convention that is sound at the row level became misleading once aggregated, because the
denominator absorbed a component the instrument had explicitly declined to key. Any
future version of this table should either exclude vacuous-gold pairs from STS and $Y$
denominators while keeping them in the coverage count, or print the evaluable $n$ beside
the mean.

### Disposition

Recorded only. Not corrected in the submitted artifact, and the tag `paper2-frozen` is
not moved. If Paper 2 is revised or extended, apply the 7-pair figure and the
"17 evaluable" phrasing, and state the vacuity convention explicitly so that Paper 2 and
Paper 3 agree.
