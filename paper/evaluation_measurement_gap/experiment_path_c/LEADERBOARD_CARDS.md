# Path C — 8-slot cards on numbers people already cite

Practice layer. **Not a result.** Fill only from the cited paper/leaderboard snapshot; blank stays UNCERTAIN. UNCERTAIN is not a finding that the bench is invalid.

Cards enter the manuscript only as a short “practice” paragraph after Path A has a licensed RESULT, or as appendix for a Findings/D&B package.

---

## Card 1 — OSWorld / OSWorld-Verified (SOTA snapshot)

| Slot | Fill |
|---|---|
| 1. Target | Desktop CUA success on OSWorld(-Verified) task suite |
| 2. Measurand | Task-specific VM state vs expected files/rules |
| 3. Observation \(I\) | Official getter at episode end (not `traj.jsonl` text). Getter payload often unreleased |
| 4. Evidence | Getter output compared by metric scripts |
| 5. Correspondence | Equality / string / file match per task JSON |
| 6. Abstention | Typically none: getter-miss or empty observation is scored as FAIL |
| 7. Non-leakage | Gold is task expected state, independent of the agent answer string |
| 8. Identifiability | One-sided success rate; no ABSTAIN class in the leaderboard number |

**Cite as:** Xie et al.\ OSWorld; OSWorld-Verified leaderboard snapshot (date UNCERTAIN until filled).  
**Do not invent a current SOTA percentage here.**

Licensed Path A reading: a published FAIL can mix empty declared \(I\) with candidate-then-mismatch; \(V=0\) does not say which.  
Forbidden: “OSWorld is invalid”; “FAIL is unjustified from \(I\).”

---

## Card 2 — WebArena / WebArena-Verified

| Slot | Fill |
|---|---|
| 1. Target | Interactive web-agent task success |
| 2. Measurand | `eval.reference_answers` / `reference_url` / `program_html` |
| 3. Observation \(I\) | Last answer string, last URL, or HTML getter — family-specific |
| 4. Evidence | String/URL/HTML match; WAV adds extract → normalize → compare |
| 5. Correspondence | Exact / fuzzy / URL / structural JSON |
| 6. Abstention | Official score has no ABSTAIN; empty last-answer is FAIL |
| 7. Non-leakage | Gold in task JSON |
| 8. Identifiability | Binary success rate |

**Cite as:** Zhou et al.\ WebArena; Hattami et al.\ WebArena-Verified.  
Public WAV recorded episodes in-repo were n=2 at the `8680588` audit; do not treat that n as the bench.

---

## Card 3 — MyPCBench reported score / “perfect” cells

| Slot | Fill |
|---|---|
| 1. Target | Desktop CUA on seeded MyPCBench guest |
| 2. Measurand | Determining-set typed gold (our \(Y\)) vs screenshot rubric \(S\) |
| 3. Observation | Rubric \(S\): screenshots. Extractor: last-answer text (`3242c30`) |
| 4. Evidence | Rubric items vs typed spans in `found` |
| 5. Correspondence | Rubric judge; fail-closed unique-candidate extractor |
| 6. Abstention | Extractor can fail-close; rubric \(S=100\) has no ABSTAIN |
| 7. Non-leakage | Guest gold independent of the screenshot judge |
| 8. Identifiability | \(S=100\) with \(Y=0\) on M1a join (7/10 joinable \(S=100\); 9/9 in \(\mathcal{A}\) have \(Y=0\)) |

This card is the only one already licensed by frozen artifacts. It is not Path A.

---

## Do not

- Average the three cards.
- Headline “benchmarks are not measurement-ready.”
- Use Path C alone as a main-track contribution.
