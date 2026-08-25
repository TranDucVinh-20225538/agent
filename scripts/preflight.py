"""Check whether a host can run the MyPCBench QEMU backend, before downloading 5 GB.

Every check mirrors what agent-harness/env.py actually does at boot, including its
OVMF discovery order and its hardcoded host-forward ports. Where a check fails in
a way that is fixable by configuration, the fix is printed as an export line and
collected into host.env.sh.

    python3 scripts/preflight.py --workdir /mnt/data2/Vinh
"""

import argparse
import glob
import os
import platform
import shutil
import socket
import subprocess
import sys

# Ports env.py forwards. Deterministic, not auto-allocated: a single collision
# makes QEMU exit at once with "Could not set up host forwarding rule".
CONTROL_API_PORT = 5000
VNC_PORT = 5901
APP_PORTS = list(range(3001, 3019))
SSH_PORT = 2222

GUEST_RAM_GB = 8      # env.py: -m 8G
GUEST_CORES = 4       # env.py: -smp 4
DISK_NEED_GB = 25     # 5.1 GB base image + CoW overlay + results

rows = []
exports = []


def check(name, ok, detail, fix=None):
    rows.append(("PASS" if ok else ("WARN" if ok is None else "FAIL"), name, detail))
    if fix:
        exports.append(fix)
    return ok


def free_ram_gb():
    try:
        with open("/proc/meminfo") as f:
            info = {}
            for line in f:
                k, _, v = line.partition(":")
                info[k] = int(v.split()[0]) / (1024 * 1024)
        return info.get("MemTotal", 0), info.get("MemAvailable", 0)
    except OSError:
        return 0, 0


def port_busy(port):
    """Try to bind the way QEMU's hostfwd does, on all interfaces."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("0.0.0.0", port))
            return False
        except OSError:
            return True


def find_free_block(start, count, limit=65000):
    base = start
    while base + count < limit:
        if not any(port_busy(p) for p in range(base, base + count)):
            return base
        base += 100
    return None


def find_free_single(start, limit=65000):
    for p in range(start, limit):
        if not port_busy(p):
            return p
    return None


def discover_ovmf():
    """Replicate _discover_ovmf from env.py, including its ordering."""
    code_env = os.environ.get("MYPCBENCH_OVMF_CODE")
    if code_env:
        vars_env = os.environ.get("MYPCBENCH_OVMF_VARS") or code_env.replace("CODE", "VARS")
        if os.path.exists(code_env) and os.path.exists(vars_env):
            return code_env, vars_env, "from MYPCBENCH_OVMF_CODE"
        return None, None, f"MYPCBENCH_OVMF_CODE set but missing: {code_env}"

    search = ["/usr/share/OVMF", "/usr/share/edk2/ovmf",
              "/usr/share/edk2-ovmf/x64", "/usr/share/qemu/ovmf"]
    excluded = ("secboot", ".ms.", "snakeoil")
    found = []
    for d in search:
        for code in sorted(glob.glob(f"{d}/OVMF_CODE*.fd")):
            if any(t in os.path.basename(code).lower() for t in excluded):
                continue
            v = code.replace("CODE", "VARS")
            if os.path.exists(v):
                found.append((code, v))
    if not found:
        return None, None, "searched " + ", ".join(search)
    found.sort(key=lambda p: (0 if "_4M" in p[0] else 1, p[0]))
    return found[0][0], found[0][1], "auto-discovered"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", default=os.getcwd(),
                    help="Where the image and overlays will live")
    args = ap.parse_args()

    check("architecture", platform.machine() == "x86_64",
          f"{platform.machine()}, kernel {platform.release()}")

    kvm = os.path.exists("/dev/kvm")
    rw = kvm and os.access("/dev/kvm", os.R_OK | os.W_OK)
    check("/dev/kvm", bool(rw),
          "readable and writable" if rw else
          ("present but not writable by this user — add yourself to the kvm group"
           if kvm else "missing: the guest would fall back to TCG and take hours"))

    cores = os.cpu_count() or 0
    check("cpu cores", cores >= GUEST_CORES, f"{cores} available, guest asks for {GUEST_CORES}")

    total, avail = free_ram_gb()
    if total:
        check("memory", avail >= GUEST_RAM_GB,
              f"{avail:.0f} GB available of {total:.0f} GB, guest asks for {GUEST_RAM_GB} GB")
    else:
        rows.append(("WARN", "memory", "cannot read /proc/meminfo on this platform"))

    if os.path.isdir(args.workdir):
        free = shutil.disk_usage(args.workdir).free / (1024 ** 3)
        check(f"disk at {args.workdir}", free >= DISK_NEED_GB,
              f"{free:.0f} GB free, need about {DISK_NEED_GB} GB")
    else:
        check(f"disk at {args.workdir}", False, "directory does not exist")

    for tool, pkg in (("qemu-system-x86_64", "qemu-system-x86"), ("qemu-img", "qemu-utils")):
        path = shutil.which(tool)
        ver = ""
        if path:
            try:
                out = subprocess.run([path, "--version"], capture_output=True,
                                     text=True, timeout=10).stdout
                ver = " " + out.splitlines()[0].split("version")[-1].strip()
            except Exception:
                pass
        check(tool, bool(path), (path or f"not installed: apt install {pkg}") + ver)

    code, vars_, how = discover_ovmf()
    check("OVMF firmware", bool(code),
          f"{code} ({how})" if code else f"not found — apt install ovmf. {how}")
    if code and how == "auto-discovered" and "_4M" not in code:
        rows.append(("WARN", "OVMF variant",
                     f"using {os.path.basename(code)}; the 4MB split is preferred when present"))

    py = sys.version_info
    check("python", py >= (3, 10), f"{py.major}.{py.minor}.{py.micro}")

    check("tmux", bool(shutil.which("tmux")),
          "present — run the harness inside it, or an SSH drop kills the run"
          if shutil.which("tmux") else "not installed; on an SSH host a disconnect "
          "would kill the runner mid-task")

    # Ports. env.py hardcodes these and only shifts them via env vars.
    busy_app = [p for p in APP_PORTS if port_busy(p)]
    busy_other = {n: p for n, p in
                  (("api", CONTROL_API_PORT), ("vnc", VNC_PORT), ("ssh", SSH_PORT))
                  if port_busy(p)}

    if not busy_app and not busy_other:
        check("ports 3001-3018, 5000, 5901, 2222", True, "all free")
    else:
        detail = []
        if busy_app:
            detail.append("app ports in use: " + ",".join(str(p) for p in busy_app))
        if busy_other:
            detail.append("also in use: " + ", ".join(f"{n}={p}" for n, p in busy_other.items()))
        rows.append(("WARN", "ports", "; ".join(detail) + " — remapping below"))

        if busy_app:
            base = find_free_block(13001, len(APP_PORTS))
            if base:
                for i, cp in enumerate(APP_PORTS):
                    exports.append(f"export MYPCBENCH_HOST_APP_PORT_{cp}={base + i}")
            else:
                rows.append(("FAIL", "ports", "no free block of 18 consecutive ports"))
        if "api" in busy_other:
            exports.append(f"export MYPCBENCH_HOST_API_PORT={find_free_single(15000)}")
        if "vnc" in busy_other:
            exports.append(f"export MYPCBENCH_HOST_VNC_PORT={find_free_single(15901)}")
        if "ssh" in busy_other:
            exports.append(f"export MYPCBENCH_HOST_SSH_PORT={find_free_single(12222)}")

    width = max(len(n) for _, n, _ in rows)
    print()
    for status, name, detail in rows:
        print(f"  [{status}] {name.ljust(width)}  {detail}")

    if exports:
        with open("host.env.sh", "w") as f:
            f.write("# Generated by scripts/preflight.py\n")
            f.write("\n".join(exports) + "\n")
        print(f"\n  Wrote host.env.sh with {len(exports)} override(s). "
              "Source it before every run:\n    source host.env.sh")

    print("""
  One thing preflight cannot fix for you, on a machine reachable over SSH:

  env.py forwards every port with `hostfwd=tcp::PORT`, which binds 0.0.0.0, so
  the 18 app ports and the Control API are exposed on every interface. The
  Control API executes arbitrary shell commands in the guest with no auth. On a
  shared or internet-facing host, bind them to loopback first — in env.py's
  _start_qemu, the hostfwd strings become tcp:127.0.0.1:PORT instead of
  tcp::PORT. Reach the desktop through an SSH tunnel rather than the open port:

    ssh -N -L 5901:127.0.0.1:5901 -L 5000:127.0.0.1:5000 user@host
""")

    failed = sum(1 for s, _, _ in rows if s == "FAIL")
    print(f"  {failed} blocking problem(s).\n" if failed else "  Ready.\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
