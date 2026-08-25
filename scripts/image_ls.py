"""List directories and read files inside the disk image, read-only.

    PYTHONPATH=vendor python3 scripts/image_ls.py --ls /data
    PYTHONPATH=vendor python3 scripts/image_ls.py --cat /etc/hostname
    PYTHONPATH=vendor python3 scripts/image_ls.py --find 'dinoco' --under /opt
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "scripts"))

import pyfsext  # noqa: E402

from qcow2 import Qcow2Reader, Window, partitions  # noqa: E402


def root_volume(image: Path):
    reader = Qcow2Reader(str(image))
    best = None
    for index, start, length in partitions(reader):
        window = Window(reader, start, length)
        window.seek(1024)
        if window.read(58)[56:58] != b"\x53\xef":
            continue
        if best is None or length > best[1]:
            best = (start, length)
    if best is None:
        raise SystemExit("no ext filesystem found")
    volume = pyfsext.volume()
    volume.open_file_object(Window(reader, best[0], best[1]))
    return volume


def kind(entry) -> str:
    try:
        if entry.get_symbolic_link_target():
            return "link"
    except Exception:
        pass
    return "dir" if entry.number_of_sub_file_entries else "file"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path, default=ROOT / "vm" / "michael_scott.qcow2")
    parser.add_argument("--ls")
    parser.add_argument("--cat")
    parser.add_argument("--find")
    parser.add_argument("--under", default="/")
    parser.add_argument("--depth", type=int, default=4)
    args = parser.parse_args()

    volume = root_volume(args.image)

    if args.ls:
        entry = volume.get_file_entry_by_path(args.ls)
        if entry is None:
            raise SystemExit(f"not found: {args.ls}")
        for child in entry.sub_file_entries:
            if child.name in (".", ".."):
                continue
            marker = kind(child)
            extra = ""
            if marker == "link":
                extra = f" -> {child.get_symbolic_link_target()}"
            size = child.size if marker == "file" else 0
            print(f"{marker:<5} {size:>12,}  {child.name}{extra}")

    if args.cat:
        entry = volume.get_file_entry_by_path(args.cat)
        if entry is None:
            raise SystemExit(f"not found: {args.cat}")
        data = b""
        while len(data) < entry.size:
            chunk = entry.read_buffer(min(1 << 20, entry.size - len(data)))
            if not chunk:
                break
            data += chunk
        sys.stdout.write(data.decode("utf-8", "replace"))

    if args.find:
        needle = args.find.lower()

        def walk(entry, path, depth):
            if depth < 0:
                return
            for child in entry.sub_file_entries:
                if child.name in (".", ".."):
                    continue
                child_path = f"{path.rstrip('/')}/{child.name}"
                if needle in child.name.lower():
                    print(f"{kind(child):<5} {child_path}")
                if child.number_of_sub_file_entries:
                    walk(child, child_path, depth - 1)

        start = volume.get_file_entry_by_path(args.under)
        if start is None:
            raise SystemExit(f"not found: {args.under}")
        walk(start, args.under, args.depth)

    return 0


if __name__ == "__main__":
    sys.exit(main())
