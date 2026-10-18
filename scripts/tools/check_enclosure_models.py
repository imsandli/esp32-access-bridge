#!/usr/bin/env python3
"""Compare committed enclosure STLs with freshly generated ones.

Usage: check_enclosure_models.py <committed_dir> <generated_dir>
Meshes must be watertight, and volume and bounding box must match
(rel. volume diff < 1e-4, bounds < 0.01 mm). Exits 1 otherwise.
"""

import glob
import os
import sys

import numpy as np
import trimesh

committed, generated = sys.argv[1], sys.argv[2]
problems = []
names = sorted(os.path.basename(p) for p in glob.glob(os.path.join(committed, "accessbridge-enclosure-*.stl")))
if not names:
    problems.append("no committed STL files")
for n in names:
    g = os.path.join(generated, n)
    if not os.path.exists(g):
        problems.append(f"{n}: not generated")
        continue
    a, b = trimesh.load(os.path.join(committed, n)), trimesh.load(g)
    if not (a.is_watertight and b.is_watertight):
        problems.append(f"{n}: mesh not watertight")
    if abs(a.volume - b.volume) > 1e-4 * abs(a.volume):
        problems.append(f"{n}: volume {a.volume:.1f} != {b.volume:.1f}")
    if np.abs(a.bounds - b.bounds).max() > 0.01:
        problems.append(f"{n}: bounds differ")
if problems:
    print("Enclosure models do not match the CadQuery source:")
    print("\n".join("  " + p for p in problems))
    print("Run scripts/export-enclosure.sh and commit the result.")
    sys.exit(1)
print(f"OK: {len(names)} enclosure STL files are watertight and match the source")
