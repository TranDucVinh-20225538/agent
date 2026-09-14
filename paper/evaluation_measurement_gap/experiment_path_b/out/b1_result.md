# Path B1 RESULT — instrument-internal discard

Not E2. Not gold. `Score` is the judge's own intermediate mark.
`MAX_IMAGE=50`. Primary T=3. Sensitivity T=(2, 3, 4).
DISCARD = qualified frames after the first 50. Threshold misses are not DISCARD.

## T=2 (sensitivity)

Episodes: 1790. Cap hits: 16.
Qualified frames: 16331. Discarded after cap: 944.
Discard / qualified: 944/16331 = 0.0578.
Cap hits by agent file:
- agente_results.json: 2/299
- browser_use_results.json: 0/300
- claude_computer_use_3.5_results.json: 0/300
- claude_computer_use_3.7_results.json: 0/300
- operator_results.json: 14/300
- seeact_results.json: 0/291

## T=3 (PRIMARY)

Episodes: 1790. Cap hits: 10.
Qualified frames: 12551. Discarded after cap: 536.
Discard / qualified: 536/12551 = 0.0427.
Cap hits by agent file:
- agente_results.json: 0/299
- browser_use_results.json: 0/300
- claude_computer_use_3.5_results.json: 0/300
- claude_computer_use_3.7_results.json: 0/300
- operator_results.json: 10/300
- seeact_results.json: 0/291

## T=4 (sensitivity)

Episodes: 1790. Cap hits: 0.
Qualified frames: 4143. Discarded after cap: 0.
Discard / qualified: 0/4143 = 0.0000.
Cap hits by agent file:
- agente_results.json: 0/299
- browser_use_results.json: 0/300
- claude_computer_use_3.5_results.json: 0/300
- claude_computer_use_3.7_results.json: 0/300
- operator_results.json: 0/300
- seeact_results.json: 0/291

