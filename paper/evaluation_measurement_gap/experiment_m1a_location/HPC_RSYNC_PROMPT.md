# HPC Cursor prompt — rsync paths for 13 M1a folders

Paste everything under **PROMPT** into Cursor **on the HPC checkout**.
Do not run gold/OCR/extractor work. Paths only.

Laptop dest (create after you receive the script):

`/Users/cubo/CMU/agent/paper/evaluation_measurement_gap/experiment_m1a_location/hpc_import/`

---

## PROMPT

```
REVIEW-ONLY PATH DISCOVERY. WRITE A RSYNC SCRIPT AND A MANIFEST. STOP.

Do not OCR screenshots. Do not open PNG as evidence. Do not run 3242c30.
Do not expand to 171 legs. Do not edit the paper. Do not chmod archives
except what you write under a new folder you create:

  /tmp/m1a_rsync_out/   (or $HOME/m1a_rsync_out if /tmp is tight)

QUESTION
--------
For each of the 13 locked M1a rows, confirm the Paper-2 trajectory
directory on this host and list every file needed to reconstruct that
leg locally: traj.jsonl + all screenshot files it references.

Then write:
  1. MANIFEST.md  — one section per UNIQUE directory (not per component)
  2. rsync_m1a.sh — one rsync line per unique directory
  3. missing.txt  — any path that does not exist, plus the find you ran

POPULATION (closed — 13 rows, 11 unique traj files)
---------------------------------------------------
Note Vinh- vs Vinh. Do not rewrite those strings.

1. flash counterfactual-f010 G0 liquid_cash
   /data2/hpcshared/Vinh-/agent/results/paper2_exec/hpc-flash-small-gate0a-postpatch/counterfactual-f010/G0/counterfactual-f010/traj.jsonl

2. flash counterfactual-f013 G0 batbucks_dividends
   /data2/hpcshared/Vinh-/agent/results/paper2_exec/hpc-flash-small-gate0a-postpatch/counterfactual-f013/G0/counterfactual-f013/traj.jsonl

3. flash counterfactual-f013 G0 gringotts_savings
   SAME traj as (2)

4. flash counterfactual-f013 G1 gringotts_savings
   /data2/hpcshared/Vinh-/agent/results/paper2_exec/hpc-flash-small-gate0a-postpatch/counterfactual-f013/G1/counterfactual-f013/traj.jsonl

5. flash retrieval-f009 G1 nyc_flight_confirmation
   /data2/hpcshared/Vinh-/agent/results/paper2_exec/hpc-flash-small-gate0a-postpatch/retrieval-f009/G1/retrieval-f009/traj.jsonl

6. flash retrieval-f010 G1 host_name
   /data2/hpcshared/Vinh-/agent/results/paper2_exec/hpc-flash-small-gate0a-postpatch/retrieval-f010/G1/retrieval-f010/traj.jsonl

7. gpt aggregation-f020 G0 batbucks_cash
   /data2/hpcshared/Vinh/agent/results/paper2_exec/study2-gpt/aggregation-f020/G0/aggregation-f020/traj.jsonl

8. gpt retrieval-f009 G0 nyc_hotel_confirmation
   /data2/hpcshared/Vinh/agent/results/paper2_exec/study2-gpt/retrieval-f009/G0/retrieval-f009/traj.jsonl

9. gpt retrieval-f009 G1 nyc_flight_confirmation
   /data2/hpcshared/Vinh/agent/results/paper2_exec/study2-gpt/retrieval-f009/G1/retrieval-f009/traj.jsonl

10. flash counterfactual-f005 G1 gme_shares
    /data2/hpcshared/Vinh-/agent/results/paper2_exec/hpc-flash-small-gate0a-postpatch/counterfactual-f005/G1/counterfactual-f005/traj.jsonl

11. claude counterfactual-f005 G0 gme_avg_cost
    /data2/hpcshared/Vinh/agent/results/paper2_exec/study2-claude/counterfactual-f005/G0/counterfactual-f005/traj.jsonl

12. claude counterfactual-f005 G0 gme_shares
    SAME traj as (11)

13. flash aggregation-f020 G1 batbucks_cash
    /data2/hpcshared/Vinh-/agent/results/paper2_exec/hpc-flash-small-gate0a-postpatch/aggregation-f020/G1/aggregation-f020/traj.jsonl

IF A LISTED traj.jsonl IS MISSING
---------------------------------
Search, in order, do not invent:

  find /data2/hpcshared/Vinh-/agent/results/paper2_exec -name traj.jsonl | grep -F '<task>/<leg>/'
  find /data2/hpcshared/Vinh/agent/results/paper2_exec -name traj.jsonl | grep -F '<task>/<leg>/'
  find $HOME -path '*paper2_exec*' -name traj.jsonl 2>/dev/null | grep -F '<task>'

Record every candidate. Prefer the exact listed path if it exists.

HOW TO FIND SCREENSHOTS
-----------------------
For each existing traj.jsonl:

  DIR=$(dirname traj.jsonl)

  1. ls -la "$DIR"
  2. If traj lines contain screenshot_file / screenshot / image path fields,
     collect unique relative paths and resolve them against $DIR and
     common siblings: $DIR/screenshots, $DIR/images, $(dirname $DIR).
  3. Also list: $DIR/*.png $DIR/**/*.png (cap the find at depth 3).

The rsync unit is the UNIQUE $DIR (the folder that contains traj.jsonl),
including all PNG/JPG it needs. If screenshots live in a sibling folder
outside $DIR, add a second rsync line for that sibling and say so in
the manifest.

Do not rsync the entire paper2_exec tree. Do not rsync 171 legs.

MANIFEST.md FIELDS PER UNIQUE DIR
---------------------------------
- lane / task / leg
- components that share this traj
- traj.jsonl realpath, exists?, bytes, mtime, sha256
- n_png, total screenshot bytes
- screenshot path pattern (e.g. screenshots/0003.png)
- DEST relative path on the laptop:

    experiment_m1a_location/hpc_import/<lane>/<task>/<leg>/

rsync_m1a.sh
------------
Use rsync -aP. Source = this host. Destination placeholder:

  LAPTOP="${LAPTOP:-user@laptop:}"
  BASE="${BASE:-/Users/cubo/CMU/agent/paper/evaluation_measurement_gap/experiment_m1a_location/hpc_import}"

One stanza per unique dir:

  rsync -aP --relative \
    /data2/hpcshared/.../<task>/<leg>/<task>/ \
    "$LAPTOP:$BASE/<lane>/<task>/<leg>/"

If --relative is messy, rsync the directory contents into that dest.
Comment the exact mkdir -p.

Print du -sh for the set at the end (expect tens–hundreds of MB, not tens of GB).
If any unique dir is > 2GB, STOP and report; do not pack 171 by accident.

THEN STOP. No gold search. No S/Y join. No paper edit.
```
