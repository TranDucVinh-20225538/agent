#!/usr/bin/env python3
"""Minimal PNG helpers for fake observations (no QEMU)."""

from __future__ import annotations

import struct
import zlib
from typing import Tuple


def solid_png(width: int = 1280, height: int = 800, rgb: Tuple[int, int, int] = (32, 64, 96)) -> bytes:
    """Return a valid solid-color PNG (IHDR+IDAT+IEND)."""
    r, g, b = rgb
    raw = b"".join(b"\x00" + bytes([r, g, b]) * width for _ in range(height))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
