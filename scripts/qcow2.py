"""Minimal read-only qcow2 decoder that handles compressed clusters.

The shipped image stores almost every cluster zlib-deflated (177,156 clusters,
nearly all with the compressed flag set). The libqcow reader returns zeros for
those, so the filesystem looks empty. This decoder resolves the L1/L2 tables and
inflates compressed clusters, and exposes a plain read/seek interface so an ext4
reader can be layered on top.
"""

from __future__ import annotations

import struct
import zlib
from collections import OrderedDict


class Qcow2Reader:
    def __init__(self, path: str, cache_clusters: int = 512):
        self._fh = open(path, "rb")
        header = self._fh.read(112)
        if header[:4] != b"QFI\xfb":
            raise ValueError("not a qcow2 file")
        (self.version,) = struct.unpack(">I", header[4:8])
        (self.cluster_bits,) = struct.unpack(">I", header[20:24])
        (self.size,) = struct.unpack(">Q", header[24:32])
        (self.l1_size,) = struct.unpack(">I", header[36:40])
        (self.l1_offset,) = struct.unpack(">Q", header[40:48])
        (incompatible,) = struct.unpack(">Q", header[72:80])
        if incompatible & ~0x1:
            raise ValueError(f"unsupported incompatible features {incompatible:#x}")

        self.cluster_size = 1 << self.cluster_bits
        self._l2_entries = self.cluster_size // 8
        self._l2_span = self._l2_entries * self.cluster_size
        self._csize_shift = 62 - (self.cluster_bits - 8)
        self._csize_mask = (1 << (self.cluster_bits - 8)) - 1
        self._offset_mask = (1 << self._csize_shift) - 1

        self._fh.seek(self.l1_offset)
        self._l1 = struct.unpack(f">{self.l1_size}Q", self._fh.read(self.l1_size * 8))
        self._l2_cache: dict[int, tuple] = {}
        self._cluster_cache: OrderedDict[int, bytes] = OrderedDict()
        self._cache_limit = cache_clusters
        self._pos = 0

    # --- cluster resolution -------------------------------------------------

    def _l2_table(self, l1_index: int):
        cached = self._l2_cache.get(l1_index)
        if cached is not None:
            return cached
        entry = self._l1[l1_index] & 0x00FFFFFFFFFFFE00
        if not entry:
            table = ()
        else:
            self._fh.seek(entry)
            table = struct.unpack(
                f">{self._l2_entries}Q", self._fh.read(self.cluster_size)
            )
        self._l2_cache[l1_index] = table
        return table

    def _cluster(self, index: int) -> bytes:
        cached = self._cluster_cache.get(index)
        if cached is not None:
            self._cluster_cache.move_to_end(index)
            return cached

        virtual = index * self.cluster_size
        l1_index = virtual // self._l2_span
        data = b"\x00" * self.cluster_size

        if l1_index < self.l1_size:
            table = self._l2_table(l1_index)
            if table:
                descriptor = table[(virtual % self._l2_span) // self.cluster_size]
                if descriptor & (1 << 62):
                    host = descriptor & self._offset_mask
                    sectors = ((descriptor >> self._csize_shift) & self._csize_mask) + 1
                    self._fh.seek(host)
                    raw = self._fh.read(sectors * 512)
                    try:
                        data = zlib.decompressobj(-zlib.MAX_WBITS).decompress(
                            raw, self.cluster_size
                        )
                    except zlib.error:
                        data = b""
                    data = data.ljust(self.cluster_size, b"\x00")
                elif descriptor & 1:
                    pass  # explicit zero cluster
                else:
                    host = descriptor & 0x00FFFFFFFFFFFE00
                    if host:
                        self._fh.seek(host)
                        data = self._fh.read(self.cluster_size).ljust(
                            self.cluster_size, b"\x00"
                        )

        self._cluster_cache[index] = data
        if len(self._cluster_cache) > self._cache_limit:
            self._cluster_cache.popitem(last=False)
        return data

    # --- file-like interface ------------------------------------------------

    def read(self, size=None) -> bytes:
        if size is None or size < 0:
            size = self.size - self._pos
        size = max(0, min(size, self.size - self._pos))
        out = bytearray()
        pos = self._pos
        while size:
            index, offset = divmod(pos, self.cluster_size)
            take = min(self.cluster_size - offset, size)
            out += self._cluster(index)[offset:offset + take]
            pos += take
            size -= take
        self._pos = pos
        return bytes(out)

    def seek(self, offset: int, whence: int = 0) -> int:
        if whence == 0:
            self._pos = offset
        elif whence == 1:
            self._pos += offset
        else:
            self._pos = self.size + offset
        return self._pos

    def tell(self) -> int:
        return self._pos

    def get_size(self) -> int:
        return self.size

    def close(self) -> None:
        self._fh.close()


class Window:
    """A byte range of a reader, presented as its own file-like object."""

    def __init__(self, reader, start: int, length: int):
        self._reader = reader
        self._start = start
        self._length = length
        self._pos = 0

    def read(self, size=None) -> bytes:
        if size is None or size < 0:
            size = self._length - self._pos
        size = max(0, min(size, self._length - self._pos))
        self._reader.seek(self._start + self._pos)
        data = self._reader.read(size)
        self._pos += len(data)
        return data

    def seek(self, offset: int, whence: int = 0) -> int:
        if whence == 0:
            self._pos = offset
        elif whence == 1:
            self._pos += offset
        else:
            self._pos = self._length + offset
        return self._pos

    def tell(self) -> int:
        return self._pos

    def get_size(self) -> int:
        return self._length


def partitions(reader) -> list[tuple[int, int, int]]:
    """Return (index, start_byte, length_byte) for each GPT partition."""
    reader.seek(512)
    header = reader.read(512)
    if header[:8] != b"EFI PART":
        raise ValueError("no GPT found")
    (table_lba,) = struct.unpack("<Q", header[72:80])
    (count,) = struct.unpack("<I", header[80:84])
    (entry_size,) = struct.unpack("<I", header[84:88])
    reader.seek(table_lba * 512)
    table = reader.read(count * entry_size)
    out = []
    for i in range(count):
        entry = table[i * entry_size:(i + 1) * entry_size]
        if entry[:16] == b"\x00" * 16:
            continue
        (first,) = struct.unpack("<Q", entry[32:40])
        (last,) = struct.unpack("<Q", entry[40:48])
        out.append((i, first * 512, (last - first + 1) * 512))
    return out
