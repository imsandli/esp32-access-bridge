#!/usr/bin/env python3
"""Compare committed fabrication outputs with freshly regenerated ones.

Usage: check_generated.py <committed_dir> <regenerated_dir>

Both directories mirror hardware/manufacturing/. Text outputs (Gerber,
Excellon, CSV, job file) must match except for lines that only carry a
generation timestamp. ZIP archives are compared member by member the same
way. Exits 1 and lists every difference otherwise.
"""

import os
import re
import sys
import zipfile

VOLATILE = re.compile(
    r"(CreationDate|Creation Date|creationDate|CreationDateTime|; *DRILL file .* date|"
    r"^G04 Created by KiCad|^; #@! TF\.CreationDate|\"CreationDate\"|^;.*date )",
    re.IGNORECASE,
)


def norm(data: bytes):
    text = data.decode("utf-8", errors="replace").replace("\r\n", "\n")
    return [ln for ln in text.split("\n") if not VOLATILE.search(ln)]


def files(root):
    out = {}
    for d, _, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            out[os.path.relpath(p, root)] = p
    return out


def main():
    a, b = files(sys.argv[1]), files(sys.argv[2])
    problems = []
    for rel in sorted(set(a) | set(b)):
        if rel.endswith(".pdf"):
            continue  # PDF plots embed dates/ids; regenerated on release
        if rel not in a or rel not in b:
            problems.append(f"{rel}: {'missing in repo' if rel not in a else 'not regenerated'}")
            continue
        if rel.endswith(".zip"):
            za, zb = zipfile.ZipFile(a[rel]), zipfile.ZipFile(b[rel])
            if sorted(za.namelist()) != sorted(zb.namelist()):
                problems.append(f"{rel}: different members")
                continue
            for m in za.namelist():
                if norm(za.read(m)) != norm(zb.read(m)):
                    problems.append(f"{rel}:{m}: content differs")
            continue
        if norm(open(a[rel], "rb").read()) != norm(open(b[rel], "rb").read()):
            problems.append(f"{rel}: content differs")
    if problems:
        print("Committed fabrication data does not match the KiCad sources:")
        print("\n".join("  " + p for p in problems))
        print("Run scripts/export-gerbers.sh and scripts/export-bom.sh and commit the result.")
        sys.exit(1)
    print(f"OK: {len(a)} committed fabrication files match the sources")


if __name__ == "__main__":
    main()
