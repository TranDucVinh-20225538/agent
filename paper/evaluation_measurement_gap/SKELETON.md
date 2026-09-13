# Full-paper skeleton (12–16 pages, venue unset)

**Argument, not an experiment dump.** Abstract last. Related work = bibliography inventory only.

Target length: 12–16 pages in 11pt article. Do not compress to AAMAS 8.

```
                 RELIABILITY CLAIM
                       │
                       ▼
              P1  score ≠ outcome
                       ▼
              P2  evaluator changes the claim
                       ▼
              P3  evidence can be lost
                       ▼
              P4-B/C/C2/D  construction reveals bounds
                       ▼
              P4-M  what claims are justified?
                       ▼
              Ext.  public artifacts ≠ measurement-ready
                       ▼
              Three gaps + eight-point reporting checklist
```

## Section plan

| § | Title | Pages (approx) | Job | Must include | Must not |
|---|---|---|---|---|---|
| 1 | Introduction | 1.0–1.5 | Problem, one real example, thesis | Pipeline; P4-B 40 DONE / 30 ABSTAIN as the easy example; thesis sentence | Open with “we propose a metric”; invent a transaction episode |
| 2 | Reliability as a measurement problem | 1.0–1.5 | Formal \( \tau\to I\to P\to E\to Y\to S \); \(\neg Justifiable \neq False\) | Claim-justification object; introduce P4-M without calling it a metric | New score \(R\) |
| 3 | Study 1 — score/outcome dissociation | 1.0–1.5 | Motivation | 24 valid pairs; per-lane table; Type A/B | Pooled rate; add n to Study 2 |
| 4 | Study 2 — functional audit | 1.5 | Evaluator consequences | Coverage 9/8/1; Y=0 on 18; selection not evaluated; 4-task exploratory; completion bias | Rank agents on 57 |
| 5 | Study 3 — where information is lost | 2.0 | Empirical core | 39/59; M1–M4; **failed repairs**; C7 existence; 9/30 | Ship a repair; Gate 0 revival |
| 6 | Study 4 — constructive validation | 2.0 | Four bounds | B completion≠evidence; C channel; C2 Form≠CC; D W1 | “Four failed metrics” |
| 7 | Claim justification (P4-M) | 1.0–1.5 | Theory | \(\mathcal{M}\); Observable_τ vs I; measurement loss | Empirical proof of P4-M |
| 8 | Typed correspondence soundness | 0.8 | Narrow lemma + “does not establish” | HIT \(\Rightarrow\) typed match; NL out of scope | Strong validity |
| 9 | External validation as eligibility boundary | 0.6 | Transportability audit | STOP wording from RESULT.md | WebArena agent indictment |
| 10 | Unified discussion | 1.0 | Three gaps | Outcome / observation / justification | “All metrics suffer equally” |
| 11 | A general reporting framework | 0.8 | Eight questions | Checklist | New instrument |
| 12 | Limitations | 0.5 | Honest | Ledger G-* | |
| 13 | Conclusion | 0.4 | Closing sentence | User’s last sentence | Abstract here |

## Order of writing (this pass)

1. Evidence map + ledger (done)
2. Body §§1–13 without abstract
3. Related-work **inventory** slotted after §2 or before §10 (short; bib-only)
4. Abstract: **not this pass**

## Split vs merge

This manuscript **is** the full programme paper. The AAMAS 8-pager stays a separate, frozen P1–P3 artifact. Do not delete it; do not copy its abstract into this file.
