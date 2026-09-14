# §0.5 parity note

Same **qcow2 pin** and **seed/matrix**, not the same host process.

| Lane | Host family | git | parser | max_steps | qcow2 sha | seed |
|---|---|---|---|---|---|---|
| GPT | node30 (frozen tree under `/data2/hpcshared/Vinh/agent`) | e8f6289 | Study2 matrix plumbing | 80 | `7c2ddcf2c2e180d07af3a7971b97d45746605005040d74271fb3e494d2f43f59` | 20260904 |
| Claude | node30 same tree | e8f6289 | Study2 matrix plumbing | 80 | `7c2ddcf2c2e180d07af3a7971b97d45746605005040d74271fb3e494d2f43f59` | 20260904 |
| Flash | HPC bright92/node002 QEMU 8.2.2 TCG (no KVM) | `0773242` dirty Alibaba pin | near_miss_xml ON; OpenRouter `only=alibaba` from ~leg 16 | 80 | `7c2ddcf2c2e180d07af3a7971b97d45746605005040d74271fb3e494d2f43f59` | 20260904 |

Host split is recorded, not papered over. Pre-patch Flash 29/57 is not in this corpus.
