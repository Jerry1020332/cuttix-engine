#!/usr/bin/env python3
"""Render the Cuttix icon set over assets/icons (the paths the build reads).

Source: cuttix/icon.png (1024 px, square). If it is missing, a placeholder
mark is drawn: a dark rounded square with a white play triangle cut by a
diagonal gap - "a clip, cut". Replace cuttix/icon.png with the final design
and run this again.
"""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "cuttix" / "icon.png"
OUT = ROOT / "assets" / "icons"


def placeholder(size=1024):
    s = size
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = int(s * 0.06)
    d.rounded_rectangle([pad, pad, s - pad, s - pad], radius=int(s * 0.22), fill=(24, 24, 27, 255))
    # Play triangle.
    cx, cy, r = s * 0.53, s * 0.5, s * 0.25
    tri = [(cx - r * 0.8, cy - r), (cx - r * 0.8, cy + r), (cx + r, cy)]
    d.polygon(tri, fill=(255, 255, 255, 255))
    # The cut: a diagonal gap through it.
    w = s * 0.045
    x0, y0, x1, y1 = s * 0.58, s * 0.22, s * 0.40, s * 0.78
    d.line([(x0, y0), (x1, y1)], fill=(24, 24, 27, 255), width=int(w))
    return img


def main():
    src = Image.open(SRC).convert("RGBA") if SRC.exists() else placeholder()
    if not SRC.exists():
        src.save(SRC)
    OUT.mkdir(parents=True, exist_ok=True)
    for n in (16, 32, 64, 128, 256, 512):
        src.resize((n, n), Image.LANCZOS).save(OUT / f"concat_logo_{n}.png")
    src.save(OUT / "concat.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])


if __name__ == "__main__":
    main()
