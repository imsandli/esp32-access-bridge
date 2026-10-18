#!/usr/bin/env python3
"""Derive JLCPCB assembly files from the KiCad BOM and position export.

Usage: jlcpcb.py <bom-full.csv> <kicad-pos.csv> <jlc-bom.csv> <jlc-cpl.csv> <manual.csv>

Parts whose "LCSC status" is "manual" (screw terminals, XIAO sockets, pin
header) or "pcb" (solder jumpers, mounting holes) are not machine assembled;
they go to the manual assembly list instead of the JLCPCB BOM/CPL.
"""

import csv
import sys

bom_in, pos_in, bom_out, cpl_out, manual_out = sys.argv[1:6]

with open(bom_in, newline="") as f:
    rows = list(csv.DictReader(f))

jlc_refs = set()
jlc_rows, manual_rows = [], []
for r in rows:
    refs = [x.strip() for x in r["Designator"].split(",") if x.strip()]
    status = r["LCSC status"]
    if r.get("DNP", "").strip():
        continue
    if status in ("manual",):
        manual_rows.append([r["Designator"], r["Value"], r["MPN"], r["Manufacturer"], r["Qty"], "hand-solder (THT)"])
        continue
    if status in ("pcb", ""):
        continue
    jlc_refs.update(refs)
    note = {"confirmed": "", "secondary": "C-number from secondary source: verify",
            "unverified": "select LCSC part at order time"}.get(status, status)
    jlc_rows.append([r["Value"] + (f" ({r['MPN']})" if r["MPN"] else ""), r["Designator"],
                     r["Footprint"].split(":")[-1], r["LCSC"], note])

with open(bom_out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #", "Note"])
    w.writerows(jlc_rows)

with open(manual_out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Designator", "Value", "Part", "Manufacturer", "Qty", "Assembly"])
    w.writerows(manual_rows)

with open(pos_in, newline="") as f:
    pos = list(csv.DictReader(f))
with open(cpl_out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
    for p in pos:
        if p["Ref"] not in jlc_refs:
            continue
        side = "Top" if p["Side"].lower() == "top" else "Bottom"
        w.writerow([p["Ref"], f"{float(p['PosX']):.4f}mm", f"{float(p['PosY']):.4f}mm", side,
                    f"{float(p['Rot']):.1f}"])

missing = jlc_refs - {p["Ref"] for p in pos}
if missing:
    raise SystemExit(f"parts in JLC BOM but not in CPL: {sorted(missing)}")
print(f"JLC BOM lines: {len(jlc_rows)}, CPL parts: {len(jlc_refs)}, manual lines: {len(manual_rows)}")
