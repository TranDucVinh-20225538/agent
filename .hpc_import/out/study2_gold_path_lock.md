# Study 2 gold-path lock (guest.json → d_i)

Frozen before hat-D STS aggregates. `registry_semantic_frozen.json` still has `gold_path: null`; this file is the inject-probe binding for legs in \(\mathcal{A}\).

- Gold is **per-leg** from that cell’s `*.guest.json` (G0 ≠ G1 when inject moved the probe).
- Lock paths named `probe_before` / `extra_probes` mean **this leg’s world**:
  - G0: `probe_before` + `extra_probes`
  - Injected G1: `probe_after` + `extra_probes_after` (pre-inject snapshot is not gold)
- Those columns may be JSON strings; parse then index.
- Missing path → `gold=null` → match bit 0 (fail-closed).
- `preference_inference-f010`: **no frozen latency/fastest formula** on timestamp lists → both components `gold=null` (do not invent a median-gap).
- `jamaica_hotel_total`: probe returns all Jamaica Sandals rows → **sum** `total_price` (component is a total).
- `sandals_jamaica_confirmation`: row whose `property_name` contains `montego` (casefold).
- `nyc_flight_confirmation`: Odds/Dinoco extra row whose `departure_date` equals hotel `check_in`.
- `oddsmarket_gme_yes`: state `{shares: integer, status: categorical}` from extra probe.

Do not use writer `track`. Do not read the other leg’s guest for this leg’s gold.
