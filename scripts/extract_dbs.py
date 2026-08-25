"""Pull the seeded app databases out of the MyPCBench disk image, read-only.

The image is an x86 guest, so booting it on an arm64 host would mean full
emulation. Nothing here needs the machine to run: a qcow2 reader, a GPT reader
and an ext4 reader are enough to copy /data/*.sqlite off the disk and read the
schema the intervention SQL has to target.

Usage
    PYTHONPATH=vendor python3 scripts/extract_dbs.py \\
        --image vm/michael_scott.qcow2 --out vm/data
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))

sys.path.insert(0, str(ROOT / "scripts"))

import pyfsext  # noqa: E402

from qcow2 import Qcow2Reader, Window, partitions  # noqa: E402

SEARCH_DIRS = ("/data", "/srv", "/opt", "/root", "/home")


def iter_ext_volumes(reader):
    """Yield every ext filesystem on the disk."""
    for index, start, length in partitions(reader):
        window = Window(reader, start, length)
        window.seek(1024)
        if window.read(58)[56:58] != b"\x53\xef":
            continue
        fs = pyfsext.volume()
        fs.open_file_object(Window(reader, start, length))
        yield f"partition {index}", fs


def walk(entry, path: str, depth: int, hits: list):
    """Collect .sqlite paths, staying shallow enough to finish quickly."""
    if depth < 0:
        return
    for child in entry.sub_file_entries:
        name = child.name
        if name in (".", ".."):
            continue
        child_path = f"{path.rstrip('/')}/{name}"
        if ".sqlite" in name or name.endswith((".db", ".db-wal", ".db-shm")):
            hits.append((child_path, child))
        elif child.number_of_sub_file_entries:
            walk(child, child_path, depth - 1, hits)


def find_databases(fs) -> list:
    hits: list = []
    for base in SEARCH_DIRS:
        try:
            entry = fs.get_file_entry_by_path(base)
        except Exception:
            continue
        if entry is None:
            continue
        walk(entry, base, 3, hits)
    if not hits:
        root = fs.get_root_directory()
        walk(root, "", 4, hits)
    return hits


def schema_of(path: Path) -> dict:
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    tables = {}
    try:
        names = [
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
        ]
        for table in names:
            cols = [
                {"name": r[1], "type": r[2]}
                for r in conn.execute(f'PRAGMA table_info("{table}")')
            ]
            count = conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
            tables[table] = {"columns": cols, "rows": count}
    finally:
        conn.close()
    return tables


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True, type=Path)
    parser.add_argument("--out", type=Path, default=ROOT / "vm" / "data")
    parser.add_argument("--list-only", action="store_true")
    args = parser.parse_args()

    reader = Qcow2Reader(str(args.image))
    print(f"image opened: {reader.size / 1e9:.1f} GB virtual")

    args.out.mkdir(parents=True, exist_ok=True)
    manifest = {}

    for label, fs in iter_ext_volumes(reader):
        found = find_databases(fs)
        print(f"{label}: {len(found)} database(s)")
        for db_path, entry in found:
            name = db_path.lstrip("/")
            print(f"  {db_path}  ({entry.size / 1e6:.1f} MB)")
            if args.list_only:
                continue
            link = None
            try:
                link = entry.get_symbolic_link_target()
            except Exception:
                link = None
            if link:
                print(f"    symlink -> {link}")
                manifest[name] = {"guest_path": db_path, "symlink_to": link}
                continue

            target = args.out / name
            target.parent.mkdir(parents=True, exist_ok=True)
            try:
                with open(target, "wb") as handle:
                    remaining = entry.size
                    while remaining > 0:
                        chunk = entry.read_buffer(min(4 << 20, remaining))
                        if not chunk:
                            break
                        handle.write(chunk)
                        remaining -= len(chunk)
            except OSError as exc:
                print(f"    unreadable: {exc}")
                manifest[name] = {"guest_path": db_path, "error": str(exc)}
                target.unlink(missing_ok=True)
                continue
            manifest[name] = {"guest_path": db_path}
            if target.name.endswith(".sqlite"):
                manifest[name]["schema"] = schema_of(target)

    reader.close()

    if manifest:
        path = ROOT / "out" / "db_schema.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(manifest, indent=2))
        print(f"\nwrote {path}  ({len(manifest)} databases)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
