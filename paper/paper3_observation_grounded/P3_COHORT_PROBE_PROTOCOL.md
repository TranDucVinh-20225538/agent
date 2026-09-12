# P3 — cohort probe protocol (feasibility gate)

**Status: open. Not an experiment. Not a pre-registration.**

The probe is a feasibility gate, not an empirical result. No agent
trajectory or intervention outcome is inspected during cohort construction.

Companion: `P3_COHORT_FEASIBILITY.md` (slate of 28), `P3_COMPARATIVE_GATE.md`
(n ≥ 20). P3-0 / P3-1 / P3-2 stay closed. `R` is not used. Study 2 `LABELS`
are not used. The C7 four are not in the slate. Study 2’s other eight are
not used as makeup.

---

## What this answers

One question:

> Do ≥ 20 of the locked 28 task-clusters actually satisfy the construct
> conditions, as guest-world gold, so that a comparative cohort can be
> locked before the first trajectory?

It does not answer whether any model is reliable, whether any intervention
moves a score, or whether any ordering flips.

## What is inspected

Pre-inject guest state only: `probe_before`, `extra_probes_before`, and
`files_before`. Schema dumps (names of tables and columns, no row values)
are allowed as construction.

## What is not inspected

Agent traces, last-response text, judge output, STS, ΔSTS, rankings,
`probe_after`, `files_after`, `gold_moved`, and any Paper 1 / P3-1 / P3-2
trajectory cell. Paper 2 inject-probe PASS/FAIL is not a survival input.
Those runs exist; this gate does not read their after-state.

## Survival rule (one cluster)

A slate member **survives** only if all of:

1. Every determining component declared for that cluster **before** its
   SELECT is run locks to a unique value of kind `money_usd` | `integer` |
   `entity` | `categorical`.
2. The lock path points at pre-inject guest state (Study 2 path dialect,
   plus `files_before.<path>` when the gold is a file line).
3. Gold is not null, not an SQL error, not an empty row-set, and not a
   multi-row set unless a sum/unique-value formula was declared with the
   component.
4. Flash and GPT are the pre-assigned pair (already fixed).

A cluster with any UNLOCKABLE determining component **fails**. D is not
rewritten to rescue it. Failed members are not replaced.

I1 SQL for the 16 is **not** part of this probe. If n ≥ 20 after gold-lock,
I1 is authored and hashed next, still before trajectory 1. Labels for
survivors are authored and hashed after this probe, before trajectory 1.

## Slate (frozen)

The 28 IDs in `P3_COHORT_FEASIBILITY.md`. No additions. No Study 2 makeup.
No preference / sealed / `contradiction-f024`.

## Two waves

**Wave A — the 12** that already have construction guest files. Evaluate
`probe_before` / `extra_probes_before` / `files_before` only. Do not re-run
inject. Do not open `probe_after`.

**Wave B — the 16.** Determining components and SELECT text are declared in
`p3_cohort_slate16_probes.json` **before** the guest boot. One dummy guest.
SELECT-only. Snapshot never patched. If a database’s schema is unknown,
dump schema (no `SELECT *`) then freeze SQL, then run; do not edit SQL
after seeing values.

HPC boots 14:26 (`qemu-img`) and 14:29 (stale `MYPCBENCH_OVMF_CODE`
under `/mnt/data2/Vinh/...`) are **TECHNICAL_ABORT**, not scores.
`.env` on this tree still carries node30 paths. `p3_cohort_hpc_guest_env.sh`
drops any guest path that is not on disk, then resolves qcow2 / OVMF /
QEMU from the HPC tree Study 2 already used. `apply_gate` stays off
until `wave_b.json` status is `SCORED`.

On HPC, tree `/data2/hpcshared/Vinh-/agent` (no agent keys):

```bash
cd /data2/hpcshared/Vinh-/agent
export AGENT_ROOT=/data2/hpcshared/Vinh-/agent
bash scripts/p3_cohort_wave_b.sh
python3 scripts/p3_cohort_apply_gate.py
```

## Stop

After both waves are scored:

* survivors ≥ 20 → **YES**. Lock that survivor list as the cohort. Then
  write labels, then I1, then a comparative pre-registration. Then, and
  only then, trajectory 1.
* survivors < 20 → **NO**. Comparative branch closed for this
  archive/cohort. C7 remains existence. Write path A. Threshold stays 20.

Do not lower 20. Do not top up the slate after seeing which probes passed.

## What this file does not authorise

Trajectories. A P3-3 experiment spec. Enlarging `R`. G3. Sealed. Looking
at intervention movement to pick a nicer 20.
