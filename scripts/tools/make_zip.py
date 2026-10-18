#!/usr/bin/env python3
"""Create a deterministic ZIP (sorted entries, fixed timestamps) from directories.

Usage: make_zip.py <out.zip> <dir> [<dir> ...]
Files are stored flat (JLCPCB expects all Gerber/drill files at the top level).
"""

import os
import sys
import zipfile

out, dirs = sys.argv[1], sys.argv[2:]
files = []
for d in dirs:
    for name in sorted(os.listdir(d)):
        path = os.path.join(d, name)
        if os.path.isfile(path) and not name.endswith(".pdf"):
            files.append((name, path))

with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for name, path in sorted(files):
        info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        with open(path, "rb") as f:
            z.writestr(info, f.read())
print(f"{out}: {len(files)} files")
