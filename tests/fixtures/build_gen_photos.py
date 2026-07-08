"""Minimal 1x1 PNG for generator tests."""
from pathlib import Path

# Valid 1x1 RGBA PNG.
MINIMAL_PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000a49444154789c63000100000500010d0a2db40000000049454e44ae426082"
)

OUT_CLOSE = Path(__file__).with_name("gen_photo_close.png")
OUT_FAR = Path(__file__).with_name("gen_photo_far.png")

for path in (OUT_CLOSE, OUT_FAR):
    path.write_bytes(MINIMAL_PNG)
    print(f"Wrote {path}")
