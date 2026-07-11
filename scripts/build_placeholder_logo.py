"""Write branding/j2_logo_placeholder.png — neutral navy block, not real J2 art."""
from __future__ import annotations

import struct
import zlib
from pathlib import Path

WIDTH = 480
HEIGHT = 160
BG = (0x1F, 0x4E, 0x79)
FG = (0xFF, 0xFF, 0xFF)
ACCENT = (0xA8, 0xC5, 0xE2)

OUT = Path(__file__).resolve().parent.parent / "branding" / "j2_logo_placeholder.png"


def _chunk(tag: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def _pixel_row(y: int) -> bytes:
    row = bytearray()
    for x in range(WIDTH):
        # Outer frame
        if x < 4 or x >= WIDTH - 4 or y < 4 or y >= HEIGHT - 4:
            color = FG
        # Simple mark box on the left
        elif 24 <= x <= 88 and 40 <= y <= 120:
            on_border = x in (24, 25, 87, 88) or y in (40, 41, 119, 120)
            on_diag = abs((x - 40) - (y - 56)) <= 1 or abs((72 - x) - (y - 56)) <= 1
            if 40 <= y <= 104 and 40 <= x <= 72 and (on_border or on_diag):
                color = FG
            elif on_border:
                color = FG
            else:
                color = BG
        # Horizontal wordmark bars (stand-in for text)
        elif 110 <= x <= 320 and 55 <= y <= 75:
            color = FG
        elif 110 <= x <= 280 and 95 <= y <= 108:
            color = ACCENT
        else:
            color = BG
        row.extend(color)
    return b"\x00" + bytes(row)


def build() -> None:
    raw = b"".join(_pixel_row(y) for y in range(HEIGHT))
    ihdr = struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(raw, 9))
        + _chunk(b"IEND", b"")
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(png)
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    build()
