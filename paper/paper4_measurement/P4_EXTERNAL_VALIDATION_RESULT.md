# P4-M external validation — result

**STATUS:** STOP
**RESULT CLASS:** no eligible independently sourced trajectory corpus under frozen \(I\to P\to E\)
**This file is not a proof of P4-M, not a metric comparison, and not an agent ranking.**

---

## Question

Can the P4-M observation/evidence distinction be transported to an independently sourced CUA trajectory corpus **without changing** the \(I\to P\to E\) pipeline after seeing outcomes?

This is transport / instantiation. It cannot prove P4-M. Typed Soundness remains a no-leakage lemma, not strong validity. NL denotation remains out of scope.

## Corpus

**None admitted.**

Candidates audited from public documentation and in-repo-absent local files:

1. WebArena-Verified (`ServiceNow/webarena-verified`, `main` `6473f72d…`) — 812 **task** specs + 2 demo evaluator/HAR logs.
2. Official WebArena (`web-arena-x/webarena`, `main` `dce04686…`) — 812 **task** specs; human/experiment traces documented as Playwright/HTML/screenshot zips on Google Drive (**not fetched**).
3. Other named HF dumps (`Sean1999/webarena`, `HaoranLiu/WebArena`, `toeunkim/matm-trajectories`, `cx-cmu/agent_trajectories`) — cards only; no download.

P4-B/C/C2/D and P1–P3 trajectories are ineligible by the frozen design.

## Eligibility

**FAIL.** See `external_validation/PHASE1_ELIGIBILITY_AUDIT.md`.

WebArena-Verified does not qualify merely because it exists. The public release is a task+evaluator specification. It does not supply \(N\ge 30\) per-episode trajectories whose declared channel is the **final assistant natural-language message**. Demo `agent_response.json` is structured evaluator JSON (`task_type` / `status` / `retrieved_data`), not that channel. Evaluators also consume `network.har`.

Official WebArena `string_match` specs contain a `reference_answers` **field** (335/335), which is a candidate independent \(L\) *if* an admissible \(\tau\) and typed \(k\) existed. They do not, in this repository, as a frozen final-text dump. Drive traces are published as DOM/screenshot/Playwright bundles. Kind \(k\) is **not** a field of the task JSON; `string_match` is an evaluator type, not \(\mathrm{kind}(L)\).

Where public documentation was insufficient to establish a required field, the field was recorded as **not established**, not inferred.

## Sample construction

**Not performed.** Frame = 0 eligible episodes. No salt, no hash draw, no IDs.

Rule that would have applied if a frame existed: \(N=30\) if \(30\le n<50\); \(N=50\) if \(n\ge 50\); prefer STOP if \(n<20\). WAV public logs n=2 would have stopped on that rule even if the channel had been NL.

## Frozen \(I/P/E/L\)

| Piece | This study |
|---|---|
| \(I\) | Final assistant NL message only (design lock). **Not instantiated** on an external \(\tau\). |
| \(P\) | Frozen `p4_instrument_v2.py` / `score_v2`. **Not modified. Not run on an external sample.** |
| \(E\) | DETERMINING iff \(\mathrm{parse}_k(s)\neq\bot\). **Not applied.** |
| \(L\) | From task spec, not agent/eval copy. Spec fields exist on some WebArena tasks; **not paired** to admissible episodes. |
| \(\leftrightarrow_k\) | Frozen `v3_match` family. **Not applied.** |

DFC `CLAIM:` syntax was not required of an external agent, and no external agent text was scored. No adapter was written. Mapping HAR, action JSON, screenshots, or scraped HTML into \(I\) would have been a scientific change of \(I\), which is STOP/KILL — not done.

## Non-leakage audit

See `external_validation/PRE_OUTCOME_NONLEAKAGE_AUDIT.md`.

No sample. No \(Y\). WAV `eval_result.json`, WebArena `merge_log.txt`, and HF `SCORES.json` were not opened. Frozen instruments were not edited after (or before) outcomes, because outcomes were not computed.

## A/B/C definitions (not applied)

| Code | Meaning |
|---|---|
| **A** | Unique typed candidate + determining \(E\) + independent \(L\) so \(Y\in\{\mathrm{HIT},\mathrm{MISS}\}\) |
| **B** | Kind-\(k\) fragment in \(\tau\) not recovered by frozen \(I/P\) (measurement loss) |
| **C** | Required stage cannot be exposed (no final text / no \(k\) / no independent \(L\)) |

B/C are not agent failure. They were **not counted**, because no episodes were sampled.

## Results

| Quantity | Value |
|---|---|
| \(N\) | n/a |
| A | n/a |
| B | n/a |
| C | n/a |
| HIT | n/a |
| MISS | n/a |

Do not interpret n/a as zero MISS, zero loss, or “all C on a hidden sample.”

## Boundary cases

The **study-level** boundary is: no public dump simultaneously provided independent source, per-episode \(\tau\), declared final-NL \(I\), typed \(k\), independent last-text \(L\), \(N\ge 30\), and offline replay without docker/live sites/parser change.

That is a **transport boundary / eligibility stop**, not a taxonomy cell inside a table.

## Limitations

- Eligibility used public docs plus two GitHub task JSONs and one demo schema file. Large Drive/HF trajectory archives were **not** downloaded. If a qualifying dump exists behind a gate or Drive folder, this pass did **not** instantiate it, and did not infer that it qualifies.
- Task-spec `reference_answers` / `retrieved_data` field presence is not a kind lock and is not a trajectory.
- Frozen `score_v2` still locates a `CLAIM:` line. The design treats DFC syntax as interface, not as permission to rewrite \(P\). Because no NL channel was admitted, that tension was **not** resolved empirically (and must not be resolved by editing the instrument).

## Conclusion

**Conservative interpretation (stop as the result):**

The overnight study **could not start transport**. No independently sourced public CUA trajectory corpus met the frozen eligibility table under the declared observation channel (final assistant natural-language message only) without changing \(I\to P\to E\), standing up WebArena/docker/live sites, running agents, or treating evaluator/HAR/screenshot/action-JSON artifacts as \(I\).

This is **not**:

- “P4-M is proven”
- “P4-M is universally valid” / “P4-M is false”
- “our metric beats existing metrics”
- “agent X is more reliable”
- “WebArena agents are unreliable”
- a MISS floor, a CC, or a reopening of P4-C/C2/D

Closest design outcome label: **STOP: no eligible public dump**, which the protocol treats as a valid scientific result of the transport check.

## Exact artifact / source hashes

Frozen instruments (unchanged):

- `p4_instrument.py` `c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59`
- `p4_instrument_v2.py` `a87ac636a729d99852eb837583b24bce372ff49c196f2be7e39e4f750622fcf3`
- `p4c2_claim_wrapper.txt` `2a028f2b95a7bc1ce815ac4b01dcb1fc7c8814ded7a5f3f38489d4ffe70e8e08`

Public specs (read-only):

- WAV dataset JSON `d65275660814663375028e9017e1f929e3c38321041b125795e2713b52243d30`
- WAV / WebArena LICENSE `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`
- WebArena `test.raw.json` `7b50386fd69163dbc05d615d834df4c6ed2c35596e97a1b10d17451c02537652`
- WAV demo 108 `agent_response.json` `c40e04ab9cefea2806b38fe2234f63dc6227e7eb055f88dd10a554b0259b3774`

Repo HEAD at audit: `c663cf8`.

## Reproducibility instructions

1. Do **not** modify frozen P4-B/C/C2/D artifacts, `p4_instrument_v2.py`, or the C2 wrapper.
2. Re-hash the three instrument files; they must match the values above.
3. Re-read `P4_EXTERNAL_VALIDATION_DESIGN.md` (unchanged protocol).
4. Optionally re-fetch the two public task JSONs and confirm sha256.
5. Confirm this workspace still contains no `*webarena*` trajectory dump.
6. Do **not** start docker, live sites, or agents to “complete” the table. That would be a new project (KILL), not a continuation of this result.

Supporting files (this workstream only):

- `paper/paper4_measurement/external_validation/PHASE0_REPO_AUDIT.md`
- `paper/paper4_measurement/external_validation/PHASE1_ELIGIBILITY_AUDIT.md`
- `paper/paper4_measurement/external_validation/SAMPLE_MANIFEST.md`
- `paper/paper4_measurement/external_validation/PRE_OUTCOME_NONLEAKAGE_AUDIT.md`
- `paper/paper4_measurement/external_validation/TRANSPORT_ANALYSIS.md`
- `paper/paper4_measurement/external_validation/PHASE6_CONSISTENCY_AUDIT.md`
- `paper/paper4_measurement/external_validation/frozen_artifact_hashes.json`
- `paper/paper4_measurement/external_validation/public_source_hashes.json`
- `paper/paper4_measurement/P4_EXTERNAL_VALIDATION_TERMINAL.md`
