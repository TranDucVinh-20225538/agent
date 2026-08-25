# Running the first counterfactual

The intervention is written and verified against the seed data extracted from the
shipped image. What is left is running an agent and the judge against a patched
environment, which needs a host that can boot the guest at usable speed.

## Host requirements

From `agent-harness/env.py` and the upstream README:

| | |
| --- | --- |
| CPU | x86-64. The guest is x86; on Apple silicon it can only be emulated. |
| Acceleration | `/dev/kvm`. Without it `env.py` falls back to `-cpu qemu64` and logs "VM will be very slow (TCG emulation)". |
| OS | Linux. The QEMU line uses `accel=kvm:tcg`, so macOS gets no acceleration even on Intel. |
| RAM | guest takes `-m 8G`, `-smp 4`, so 16 GB host is comfortable |
| Disk | ~25 GB (5.1 GB image, plus per-run overlay and results) |
| Packages | `qemu-system-x86_64`, `qemu-img`, OVMF/UEFI firmware, Python ≥ 3.10 |

A boot is about 90 seconds and a task one to three minutes once warm.

Note for an Intel Mac: it will boot but under TCG, so expect roughly an order of
magnitude slowdown. Prefer Linux, WSL2 with nested virtualisation, or a cloud
instance.

## If the host is Windows

Everything runs inside WSL2, which needs nested virtualisation to expose
`/dev/kvm`. That is a Windows 11 feature; Windows 10 cannot do it, and on
Windows 10 the options are a Linux dual boot, a live USB, or a cloud instance.

Put this in `%UserProfile%\.wslconfig`, then run `wsl --shutdown` in PowerShell:

```ini
[wsl2]
nestedVirtualization=true
memory=16GB
processors=8
```

In the Ubuntu shell, the one check that decides everything:

```bash
ls -l /dev/kvm && sudo usermod -aG kvm "$USER"   # then close and reopen the shell
sudo apt update && sudo apt install -y qemu-system-x86 ovmf python3-venv git curl
```

If `/dev/kvm` is missing, `wsl --update` first — nested virtualisation needs a
recent WSL kernel. Nothing further will work until that file exists, since
`env.py` decides on acceleration purely by `os.path.exists("/dev/kvm")`.

Two Windows-specific traps:

- Keep the image and the repo inside the Linux filesystem (`~/`), never under
  `/mnt/c`. The Windows mount goes through a translation layer and a 5 GB qcow2
  with random writes on it is painfully slow.
- Use the default `--backend qemu`, not `--backend docker`. The Docker backend
  passes `--device /dev/kvm` into a container, and Docker Desktop on Windows runs
  its own separate VM that will not hand that device through.

If boot is slow but working, raise the readiness budget rather than concluding it
failed: `export MYPCBENCH_VM_READY_TIMEOUT=1800` (default 900 s).

## Setup

```bash
git clone <this repo> && cd agent
bash scripts/setup.sh              # upstream harness + task files + image metadata

cd external/MyPCBench-main
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Step 1 — sanity run, no API keys, no cost

This proves the host can boot the guest and that the Control API answers, before
any tokens are spent.

```bash
bash scripts/get-eval-image.sh --out ./mypcbench-vm
source ./mypcbench-vm/env.sh

python3 agent-harness/run_mypcbench.py --backend qemu \
  --qcow2_path "$MYPCBENCH_QCOW2" --agent_type dummy --model dummy \
  --tasks_dir tasks/smoke_one --max_steps 4 --result_dir results/sanity
```

The image `get-eval-image.sh` fetches is the current v0.1 build. Anything meant
to be compared against the published numbers needs
`michael_scott_round78e.qcow2` (12.4 GB), the archived v0.0 labelled for paper
reproduction — but note the repo ships only the current grading file, not the
grading that produced those numbers.

## Step 2 — wire the intervention in

The patch has to land after app warm-up and before the agent's first action.
That point already exists: `_prewarm_lazy_dbs` in `agent-harness/env.py` is where
the authors run their own `UPDATE` against `/data/dinoco-airlines.sqlite`. Add
one call directly after that block, around line 1023:

```python
        cf_task = os.environ.get("MYPCBENCH_CF_TASK")
        if cf_task:
            subprocess.run(
                [sys.executable, os.environ["MYPCBENCH_CF_SCRIPT"],
                 "--api", self.base_url, "--task", cf_task],
                check=True,
            )
```

Then a run is a pair, identical except for one environment variable:

```bash
# baseline
python3 agent-harness/run_mypcbench.py --backend qemu \
  --qcow2_path "$MYPCBENCH_QCOW2" \
  --agent_type claude_cuabash --model claude-opus-4-6 \
  --tasks_dir tasks/one_retrieval_f001 --max_steps 40 \
  --result_dir results/base-retrieval-f001

# counterfactual
export MYPCBENCH_CF_TASK=retrieval-f001
export MYPCBENCH_CF_SCRIPT=/path/to/agent/scripts/cf_inject.py
python3 agent-harness/run_mypcbench.py --backend qemu \
  --qcow2_path "$MYPCBENCH_QCOW2" \
  --agent_type claude_cuabash --model claude-opus-4-6 \
  --tasks_dir tasks/one_retrieval_f001 --max_steps 40 \
  --result_dir results/cf-retrieval-f001

python3 agent-harness/judge_results.py --result_dir results/base-retrieval-f001
python3 agent-harness/judge_results.py --result_dir results/cf-retrieval-f001
```

Single-task files are already prepared in `cf/tasks/`, one per task, in the shape
`tasks/smoke_one/one.json` uses and with every field the runner expects:

```bash
mkdir -p external/MyPCBench-main/tasks/cf_one
cp cf/tasks/retrieval-f001.json external/MyPCBench-main/tasks/cf_one/one.json
# then --tasks_dir tasks/cf_one
```

They are taken from the per-bucket rubric files (`tasks/final/<app>/<app>.rubrics.json`)
rather than the compiled `all_tasks_with_grading.json`, because the compiled file
drops seven fields including `persona`, `time_limit_seconds`, `date_policy` and
`required_subtasks`.

To check the injection alone, without an agent, boot with the dummy agent and
run against the live Control API:

```bash
python3 scripts/cf_inject.py --api http://127.0.0.1:5000 --task retrieval-f001 --probe-only
python3 scripts/cf_inject.py --api http://127.0.0.1:5000 --task retrieval-f001
```

The port is whatever `env.py` reports as the discovered API port at boot.

## What the two interventions do

| task | database | intervention | gold before | gold after |
| --- | --- | --- | --- | --- |
| `retrieval-f001` | `dinoco-airlines.sqlite` | one row of `loyalty` | Gold Voyager, 38,450 miles | Silver Voyager, 8,620 miles |
| `hard_app-f033` | `hoolicalendar.sqlite` | move the Thursday improv block two hours | overlap exists, so reschedule and notify | no overlap, so report all-clear |

`situated_action-f028` is the control: it books any well-rated Scranton property
and depends on nothing in the persona's records, so it should be run under both
conditions and should not move.

Both interventions were verified against the extracted databases: the gold moves,
exactly one row changes, and no other table is touched. `cf_patch.py` and
`cf_inject.py` both record which tables moved, so each run carries that evidence.

## What to record per run

For each task and condition: the probe value before and after, the judge's
per-criterion verdicts, and the trajectory. The question is not whether the score
drops. It is whether the agent's answer tracks the new state — an agent that
still says Gold Voyager after the patch was not reading the profile.

## Traps found the hard way

- **The WAL holds the state.** Reading `/data/*.sqlite` without its `-wal` gives
  Silver Voyager and 7 flights instead of Gold Voyager and 16. Never diff the
  database files alone.
- **Timestamp format.** SQLite's `datetime()` returns a space separator while
  every stored value uses ISO `T`. Restore it or one row looks unlike every other.
- **The reseed trigger.** `/opt/mypcbench-firstboot.sh` wipes `/data/*.sqlite*`
  and regenerates if `/data/.seeded_fingerprint` does not equal
  `PERSONA:WORLD:VM_ID:::`. Do not touch that file.
- **Dates move.** The image rebases dates at boot, so anything date-dependent
  must be computed from the guest clock, not hardcoded.
- **Published digests.** `SHA256SUMS` and `VERSION.json` claim `6e2c6954…` for
  the image; the file actually served hashes to `59c9614c…`. Do not treat a
  checksum failure there as a bad download without checking the size and the
  git-lfs pointer first.
