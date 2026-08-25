"""Build mock app databases so the patch layer can be exercised without the VM.

The real schema is only knowable by opening the qcow2; `env.py` guarantees the
table names and the user_email key and nothing else. These fixtures use the
shape the intervention spec assumes, so a failing patch against the real image
localises the problem to column names rather than to the tooling.
"""

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOCK = ROOT / "out" / "mock"
EMAIL = "michael.scott@dundermifflin.com"


def dinoco(path: Path) -> None:
    conn = sqlite3.connect(path)
    with conn:
        conn.execute(
            "CREATE TABLE loyalty (user_email TEXT, tier TEXT, miles_balance INTEGER)"
        )
        conn.execute(
            "INSERT INTO loyalty VALUES (?, 'Dinoco Bronze', 3604)", (EMAIL,)
        )
    conn.close()


def hoolicalendar(path: Path) -> None:
    conn = sqlite3.connect(path)
    with conn:
        conn.execute(
            "CREATE TABLE events (id INTEGER PRIMARY KEY, user_email TEXT,"
            " title TEXT, start_at TEXT, end_at TEXT)"
        )
        # 2026-08-27 is a Thursday: an improv block overlapping a work meeting.
        conn.executemany(
            "INSERT INTO events (user_email, title, start_at, end_at) VALUES (?,?,?,?)",
            [
                (EMAIL, "Improv class", "2026-08-27 18:00:00", "2026-08-27 20:00:00"),
                (EMAIL, "Client sync with Andy and Jim", "2026-08-27 19:00:00", "2026-08-27 19:45:00"),
                (EMAIL, "Dentist", "2026-08-25 09:00:00", "2026-08-25 09:30:00"),
            ],
        )
    conn.close()


def main() -> int:
    MOCK.mkdir(parents=True, exist_ok=True)
    builders = {
        "dinoco-airlines.sqlite": dinoco,
        "hoolicalendar.sqlite": hoolicalendar,
    }
    for name, build in builders.items():
        path = MOCK / name
        if path.exists():
            path.unlink()
        build(path)
        print(f"built {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
