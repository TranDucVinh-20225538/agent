"""Deterministic string replacements for dual-channel file interventions.

Used by cf_inject.py to patch guest Files blobs. Pure functions so the
replacements can be checked without QEMU.
"""

from __future__ import annotations


def apply_replacements(text: str, pairs: list[list[str]]) -> str:
    out = text
    for pair in pairs:
        if len(pair) != 2:
            raise SystemExit(f"file patch pair must be [old, new], got {pair!r}")
        old, new = pair
        if old not in out:
            raise SystemExit(f"file patch: {old!r} not found in file")
        out = out.replace(old, new)
    return out


def check_hold_constant(text: str, needle: str | None) -> None:
    if needle and needle not in text:
        raise SystemExit(f"file patch: hold_constant {needle!r} missing after replace")


def self_test() -> None:
    src = (
        "Employer: Dunder Mifflin Paper Company, Inc.\n"
        "Box 1 - Wages, tips, other compensation: $142,000.00\n"
        "Box 2 - Federal income tax withheld:     $28,400.00\n"
        "Box 3 - Social Security wages:           $142,000.00\n"
    )
    out = apply_replacements(src, [
        ["$142,000.00", "$90,000.00"],
        ["$28,400.00", "$18,000.00"],
    ])
    assert "$90,000.00" in out
    assert "$18,000.00" in out
    assert "$142,000.00" not in out
    assert "$28,400.00" not in out
    check_hold_constant(out, "Employer: Dunder Mifflin")
    try:
        apply_replacements("nope", [["$142,000.00", "$90,000.00"]])
    except SystemExit:
        pass
    else:
        raise AssertionError("expected missing-old failure")


if __name__ == "__main__":
    self_test()
    print("cf_file_patch self-test ok")
