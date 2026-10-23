"""Packed integer value arrays for WeatherGrid browser bundles.

Browser bundles previously stored every quantized field as a JSON array of
integers; for the CWA WRF 3 km grid (234 x 267 cells x 17 fields x frames)
that text representation dominated the payload (~9.6 MB). This module packs
the quantized integer arrays as little-endian int16, gzips them, and emits a
base64 payload, cutting the transfer to roughly one eighth with no additional
runtime dependency: browsers decode it with DecompressionStream('gzip').

Format marker: {"enc": "i16gz", "data": "<base64 gzip of int16 LE>"}.
Missing quantized cells use the -32768 sentinel and decode back to None.
"""
from __future__ import annotations

import base64
import gzip
import struct

ENCODING_NAME = "i16gz"
NULL_SENTINEL = -32768
_INT16_MIN = -32767  # -32768 is reserved for the null sentinel
_INT16_MAX = 32767


def pack_int16_gz(values: list) -> dict:
    """Pack a quantized integer array (None = missing) into the i16gz entry."""
    missing = 0
    out = []
    for value in values:
        if value is None:
            out.append(NULL_SENTINEL)
            missing += 1
            continue
        number = int(value)
        if number < _INT16_MIN or number > _INT16_MAX:
            raise ValueError(f"quantized value {number} does not fit packed int16")
        out.append(number)
    raw = struct.pack(f"<{len(out)}h", *out)
    payload = base64.b64encode(gzip.compress(raw, 9)).decode("ascii")
    entry = {"enc": ENCODING_NAME, "data": payload}
    if missing:
        entry["null_cells"] = missing
    return entry


def unpack_int16_gz(entry: dict) -> list:
    """Decode an i16gz entry back into the original integer/None list."""
    if entry.get("enc") != ENCODING_NAME:
        raise ValueError(f"unsupported packed encoding: {entry.get('enc')!r}")
    raw = gzip.decompress(base64.b64decode(entry["data"]))
    ints = struct.unpack(f"<{len(raw) // 2}h", raw)
    return [None if value == NULL_SENTINEL else value for value in ints]


def is_packed_entry(value) -> bool:
    return isinstance(value, dict) and value.get("enc") == ENCODING_NAME
