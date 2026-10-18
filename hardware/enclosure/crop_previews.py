#!/usr/bin/env python3
"""Trim white margins of the preview PNGs in drawings/ (used by scripts/export-enclosure.sh)."""
import glob
import os

from PIL import Image, ImageChops

for f in glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "drawings", "enclosure-*.png")):
    im = Image.open(f).convert("RGB")
    bb = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
    if bb:
        im.crop((max(bb[0] - 20, 0), max(bb[1] - 20, 0), min(bb[2] + 20, im.width), min(bb[3] + 20, im.height))).save(f)
