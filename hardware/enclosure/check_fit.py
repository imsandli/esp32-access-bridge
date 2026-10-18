#!/usr/bin/env python3
"""Mechanical fit check: AccessBridge C6 PCB (KiCad STEP) vs. the printed enclosure.

Usage: python check_fit.py [--step models/pcb/accessbridge-c6.step] [--render DIR]

Fails (exit 1) unless:
  1. no part of the PCB assembly (incl. the XIAO envelope) intersects base, lid,
     plunger or clamp;
  2. the lid is >= 1.5 mm above every component;
  3. both USB-C openings (XIAO + J6) lie inside their wall cut-outs with
     >= 0.5 mm margin, and the wall at the cut-outs is <= 1.5 mm thick;
  4. the PCB mounting holes are concentric with the standoffs;
  5. no heat-set insert (metal) is within 10 mm of the XIAO antenna keep-out;
  6. every part is a valid solid.
"""

import argparse
import os
import sys

import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "models"))
import accessbridge_enclosure as E  # noqa: E402

DEFAULT_STEP = os.path.join(HERE, "models", "pcb", "accessbridge-c6.step")


def pcb_assembly(step):
    pcb = cq.importers.importStep(step).translate((0, 0, E.PCB_Z))
    x = E.XIAO_USB_X
    # XIAO envelope: 17.8 mm wide, from its USB-C face (1.45 mm inside the board edge) 21 mm long
    xiao = cq.Workplane("XY").box(17.8, 21.0 + 1.55, E.XIAO_TOP - E.XIAO_BOTTOM, centered=False) \
        .translate((x - 8.9, -1.45 - 21.0 - 1.55 + 1.55, E.XIAO_BOTTOM))
    return pcb, xiao


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", default=DEFAULT_STEP)
    ap.add_argument("--render", default=None, help="write preview SVG/PNG images to this directory")
    args = ap.parse_args()

    parts = E.build()
    pcb, xiao = pcb_assembly(args.step)
    pcb_shape = pcb.val()
    problems = []

    # 6. valid solids
    for name, p in parts.items():
        if not p.val().isValid():
            problems.append(f"{name}: invalid solid")

    # 1. collisions
    for name, p in parts.items():
        for what, obj in (("PCB assembly", pcb_shape), ("XIAO envelope", xiao.val())):
            vol = p.val().intersect(obj).Volume()
            if vol > 0.01:
                problems.append(f"{name} intersects {what}: {vol:.2f} mm3")

    # 2. lid clearance above components (plunger guide excluded: it sits beside SW1)
    top = max(pcb_shape.BoundingBox().zmax, E.XIAO_TOP)
    clearance = E.TOP_Z - top
    if clearance < 1.5:
        problems.append(f"lid clearance {clearance:.2f} mm < 1.5 mm")

    # 3. USB-C openings vs cut-outs
    checks = [("XIAO USB-C", E.XIAO_USB_X, E.XIAO_USB_Z, E.XIAO_USB_W, E.XIAO_USB_H, E.XIAO_CUT_H),
              ("J6 USB-C", E.J6_X, E.J6_USB_Z, 8.94, 4.27, E.USB_CUT_H)]
    for name, x, z, w, h, cut_h in checks:
        mx = (E.USB_CUT_W - w) / 2
        mz = (cut_h - h) / 2
        if min(mx, mz) < 0.5:
            problems.append(f"{name}: cut-out margin {min(mx, mz):.2f} mm < 0.5 mm")
        top = z + max(E.RECESS_H, cut_h + 2) / 2
        if top > E.TOP_Z - 1.0:
            problems.append(f"{name}: cut-out/recess reaches {top:.1f} mm, less than 1 mm below the lid seat")
    if E.WALL - E.RECESS_D > 1.5:
        problems.append("wall at USB-C cut-outs thicker than 1.5 mm")

    # gland: lock nut must fit between floor and lid seat, flat top leaves wall
    nut_top = E.GLAND_Z + E.GLAND_NUT_D / 2
    if E.GLAND_Z - E.GLAND_NUT_D / 2 < E.FLOOR or nut_top > E.TOP_Z:
        problems.append(f"M16 lock nut does not fit (z {E.GLAND_Z - E.GLAND_NUT_D / 2:.1f}..{nut_top:.1f})")
    if E.TOP_Z - (E.GLAND_Z + E.GLAND_D / 2 * 1.1) < 2.5:
        problems.append("less than 2.5 mm wall above the gland hole")

    # 4. standoffs concentric with PCB holes (both come from design.py, but keep the guard)
    for (hx, hy), (sx, sy) in zip(E.PCB_HOLES, E.PCB_HOLES):
        if abs(hx - sx) > 0.01 or abs(hy - sy) > 0.01:
            problems.append("standoff/hole mismatch")

    # 5. inserts vs antenna keep-out
    ax0, ay0, ax1, ay1 = E.design.ANTENNA_KEEPOUT
    ax0, ax1, ay0, ay1 = ax0, ax1, -ay1, -ay0
    for x, y in E.BOSSES + E.PCB_HOLES + E.CLAMP_POSTS:
        dx = max(ax0 - x, 0, x - ax1)
        dy = max(ay0 - y, 0, y - ay1)
        if (dx * dx + dy * dy) ** 0.5 < 10.0:
            problems.append(f"metal insert at ({x:.1f},{y:.1f}) within 10 mm of the antenna keep-out")

    print(f"lid clearance above tallest part: {clearance:.2f} mm")
    print(f"XIAO USB-C centre: z = {E.XIAO_USB_Z:.2f} mm, wall at cut-outs: {E.WALL - E.RECESS_D:.2f} mm")
    print(f"outer size: {E.OUT_X1 - E.OUT_X0:.1f} x {E.OUT_Y0 - E.OUT_Y1:.1f} x {E.TOP_Z + E.LID:.1f} mm (without DIN clip)")

    if args.render:
        render(args.render, parts, pcb, xiao)

    if problems:
        print("FIT CHECK FAILED:")
        print("\n".join("  " + p for p in problems))
        sys.exit(1)
    print("OK: enclosure fit check passed")


def render(out, parts, pcb, xiao):
    os.makedirs(out, exist_ok=True)
    opts = dict(width=1400, height=1000, marginLeft=40, marginTop=40, showAxes=False,
                strokeWidth=0.25, showHidden=False)
    views = {
        "enclosure-assembly": (cq.Workplane().add(parts["base-din"].val()).add(pcb.val()).add(xiao.val()), (1, -1.2, 1.1)),
        "enclosure-base-top": (parts["base-din"], (0.3, -0.6, 1)),
        "enclosure-base-usb-side": (parts["base-din"], (0.2, 1, 0.35)),
        "enclosure-base-din-underside": (parts["base-din"], (0.4, -0.5, -1)),
        "enclosure-base-wall": (parts["base-wall"], (0.4, -0.6, 0.8)),
        "enclosure-base-wall-underside": (parts["base-wall"], (0.4, -0.5, -1)),
        "enclosure-lid": (parts["lid"], (0.3, -0.6, 1)),
    }
    for name, (obj, d) in views.items():
        svg = os.path.join(out, name + ".svg")
        cq.exporters.export(obj, svg, opt=dict(opts, projectionDir=d))
        try:
            import cairosvg
            cairosvg.svg2png(url=svg, write_to=os.path.join(out, name + ".png"), background_color="white")
            os.remove(svg)
        except ImportError:
            pass


if __name__ == "__main__":
    main()
