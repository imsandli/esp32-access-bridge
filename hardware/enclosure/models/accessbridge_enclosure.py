#!/usr/bin/env python3
"""Parametric 3D-printable enclosure for AccessBridge C6 HW-1.1 / Rev B (CadQuery).

Usage:
  python accessbridge_enclosure.py [--out DIR]     export STEP + STL of all parts

Coordinate frame = the KiCad STEP export with --drill-origin: board X 0..96,
board Y 0..-56 (top edge with the USB-C ports at Y = 0, terminals at Y = -56),
PCB bottom at Z = PCB_Z (on the standoffs). PCB-dependent values (outline,
mounting holes, USB-C, LEDs, PAIR button, terminals) come from
hardware/tools/design.py, so the case follows the board.

Parts: two base variants (``base-din``: TS35 DIN-rail clip; ``base-wall``: screw
flanges), plus the shared lid, PAIR plunger and cable clamp.
Licence: CERN-OHL-S-2.0 (hardware).
"""

import argparse
import os
import sys

import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "tools"))
import design  # noqa: E402

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# --- parameters (mm) --------------------------------------------------------
WALL = 2.4            # side walls
FLOOR = 2.4           # base floor
LID = 2.4             # lid plate
STANDOFF = 5.0        # PCB standoff height above the floor
GAP = 0.6             # PCB edge to inner wall (top edge with USB-C)
SIDE_ROOM = 9.0       # inner wall to PCB left/right edge (room for lid bosses)
WIRING_ROOM = 20.0    # in front of the screw terminals
LID_CLEARANCE = 4.5   # above the tallest part (XIAO envelope); leaves wall above the XIAO USB-C cut-out
FIT = 0.3             # lid lip clearance

# Seeed XIAO ESP32C6 on 7.0 mm sockets (FREI BL 1X07G7 2,54, turned contacts):
# envelope above the socket top. The XIAO has no 3D model in the KiCad export;
# values are conservative: 2.5 mm male-header spacer + ~1.0 mm PCB + 3.3 mm USB-C/shield.
# The KiCad STEP shows 8.5 mm PinSocket models; they stay below this envelope.
SOCKET_H = 7.0
SOCKET_TOP = 1.6 + SOCKET_H   # above PCB bottom
XIAO_SPACER = 2.5
XIAO_PCB = 1.0
XIAO_TOP_PARTS = 3.3
XIAO_USB_W, XIAO_USB_H = 9.0, 3.2

PCB_T = 1.6
PCB_Z = FLOOR + STANDOFF                       # PCB bottom
XIAO_BOTTOM = PCB_Z + SOCKET_TOP + XIAO_SPACER
XIAO_TOP = XIAO_BOTTOM + XIAO_PCB + XIAO_TOP_PARTS
XIAO_USB_Z = XIAO_BOTTOM + XIAO_PCB + XIAO_USB_H / 2
J6_USB_Z = PCB_Z + 2.73                        # J6 shell centre (STEP: 0.59..4.86)
TERMINAL_TOP = PCB_Z + 15.4                    # MKDS top (STEP)
BUTTON_TOP = PCB_Z + PCB_T + 1.5               # TS-1187A, 1.5 mm actuator height (datasheet)

BW, BH = design.BOARD_W, design.BOARD_H
IN_X0, IN_X1 = -SIDE_ROOM, BW + SIDE_ROOM
IN_Y0, IN_Y1 = GAP, -(BH + WIRING_ROOM)        # top / bottom inner wall
# M16 x 1.5 lock nut across corners: SW 22 (e.g. Delock 60615) = 25.4 mm; it must
# turn freely between floor and lid, so it can also set the inner height
GLAND_NUT_D = 25.5
TOP_Z = max(max(XIAO_TOP, TERMINAL_TOP) + LID_CLEARANCE,   # inner lid surface
            FLOOR + GLAND_NUT_D + 0.6)
OUT_X0, OUT_X1 = IN_X0 - WALL, IN_X1 + WALL
OUT_Y0, OUT_Y1 = IN_Y0 + WALL, IN_Y1 - WALL

# USB-C cut-outs (in the top wall) and outside recess for plug overmolds
USB_CUT_W, USB_CUT_H = 11.5, 6.0               # receptacle 8.9 x 3.2 + margin
XIAO_CUT_H = 8.0                               # extra height tolerance for the socket stack
RECESS_W, RECESS_H, RECESS_D = 13.5, 9.5, 1.2  # wall stays WALL - RECESS_D = 1.2 mm
XIAO_USB_X = design.PCB_POS["U2"][0]
J6_X = design.PCB_POS["J6"][0]

# lid screw bosses (M3 heat-set inserts) in the inner corners, beside the PCB
BOSS_D = 8.0
INSERT_D, INSERT_DEPTH = 4.0, 6.0              # typical M3 x 5.7 brass insert
SCREW_RELIEF_D = 3.2                           # room for the screw tip below an insert
LID_RELIEF = 5.0                               # lid: M3 x 10 reaches 8.8 mm below the lid
CLAMP_RELIEF = 1.6                             # clamp posts: M3 x 12, bar on the cable
# bosses overlap the top/bottom walls by 1 mm (no tangent faces -> manifold mesh)
BOSSES = [(IN_X0 + BOSS_D / 2 + 0.4, IN_Y0 - BOSS_D / 2 + 1.0), (IN_X1 - BOSS_D / 2 - 0.4, IN_Y0 - BOSS_D / 2 + 1.0),
          (IN_X0 + BOSS_D / 2 + 0.4, IN_Y1 + BOSS_D / 2 - 1.0), (IN_X1 - BOSS_D / 2 - 0.4, IN_Y1 + BOSS_D / 2 - 1.0)]
PCB_HOLES = [(design.PCB_POS[h][0], -design.PCB_POS[h][1]) for h in ("H1", "H2", "H3", "H4")]
STANDOFF_D = 7.0

# cable entry: M16 x 1.5 gland in the terminal wall, strain-relief clamp inside
GLAND_D = 16.3
GLAND_X = 34.0
GLAND_Z = FLOOR + (TOP_Z - FLOOR) / 2
CLAMP_POSTS = [(GLAND_X - 13.0, IN_Y1 + 9.0), (GLAND_X + 13.0, IN_Y1 + 9.0)]
CLAMP_POST_D, CLAMP_POST_H = 7.0, 8.0

# lid features
LED_HOLES = [(design.PCB_POS["D4"][0], -design.PCB_POS["D4"][1]), (design.PCB_POS["D5"][0], -design.PCB_POS["D5"][1])]
LED_HOLE_D = 2.0
PAIR = (design.PCB_POS["SW1"][0], -design.PCB_POS["SW1"][1])
PLUNGER_D, PLUNGER_HOLE_D, PLUNGER_FLANGE_D, PLUNGER_FLANGE_T = 4.0, 4.5, 6.5, 1.2
PLUNGER_TRAVEL = 0.6                           # gap above the button when released

# din variant: TS35 rail clip on the floor underside (rail along X)
DIN_CY = (OUT_Y0 + OUT_Y1) / 2
DIN_LEN = 30.0
DIN_X = 48.0
RAIL_W, RAIL_T = 35.0, 1.0
# wall variant: flanges on the short sides with screw slots (box stays closed when mounting)
FLANGE_W, FLANGE_T = 11.0, 4.0
SCREW_SLOT_D, SCREW_SLOT_LEN = 4.5, 8.0        # for 4 mm wood screws / M4, slot allows alignment
VARIANTS = ("din", "wall")


def base(mount="din"):
    outer = cq.Workplane("XY").box(OUT_X1 - OUT_X0, OUT_Y0 - OUT_Y1, TOP_Z, centered=False) \
        .translate((OUT_X0, OUT_Y1, 0))
    inner = cq.Workplane("XY").box(IN_X1 - IN_X0, IN_Y0 - IN_Y1, TOP_Z, centered=False) \
        .translate((IN_X0, IN_Y1, FLOOR))
    b = outer.cut(inner)
    b = b.edges("|Z").fillet(1.5)

    # lid bosses with heat-set insert holes
    for x, y in BOSSES:
        boss = cq.Workplane("XY").circle(BOSS_D / 2).extrude(TOP_Z - FLOOR).translate((x, y, FLOOR))
        b = b.union(boss)
        b = b.cut(cq.Workplane("XY").circle(INSERT_D / 2).extrude(INSERT_DEPTH).translate((x, y, TOP_Z - INSERT_DEPTH)))
        b = b.cut(cq.Workplane("XY").circle(SCREW_RELIEF_D / 2).extrude(LID_RELIEF + 0.1)
                  .translate((x, y, TOP_Z - INSERT_DEPTH - LID_RELIEF)))
    # PCB standoffs with inserts
    for x, y in PCB_HOLES:
        so = cq.Workplane("XY").circle(STANDOFF_D / 2).extrude(STANDOFF).translate((x, y, FLOOR))
        b = b.union(so)
        b = b.cut(cq.Workplane("XY").circle(INSERT_D / 2).extrude(STANDOFF + 0.5).translate((x, y, PCB_Z - STANDOFF - 0.5)))
    # strain-relief clamp posts
    for x, y in CLAMP_POSTS:
        post = cq.Workplane("XY").circle(CLAMP_POST_D / 2).extrude(CLAMP_POST_H).translate((x, y, FLOOR))
        b = b.union(post)
        b = b.cut(cq.Workplane("XY").circle(INSERT_D / 2).extrude(INSERT_DEPTH).translate((x, y, FLOOR + CLAMP_POST_H - INSERT_DEPTH)))
        b = b.cut(cq.Workplane("XY").circle(SCREW_RELIEF_D / 2).extrude(CLAMP_RELIEF + 0.1)
                  .translate((x, y, FLOOR + CLAMP_POST_H - INSERT_DEPTH - CLAMP_RELIEF)))

    # USB-C cut-outs through the top wall + outside recesses
    for x, z, h in ((XIAO_USB_X, XIAO_USB_Z, XIAO_CUT_H), (J6_X, J6_USB_Z, USB_CUT_H)):
        cut = cq.Workplane("XZ").center(x, z).rect(USB_CUT_W, h).extrude(-WALL - 2).translate((0, IN_Y0 - 1, 0))
        b = b.cut(cut.edges("|Y").fillet(1.0))
        rec = cq.Workplane("XZ").center(x, z).rect(RECESS_W, max(RECESS_H, h + 2)).extrude(-RECESS_D - 1) \
            .translate((0, OUT_Y0 - RECESS_D, 0))
        b = b.cut(rec.edges("|Y").fillet(1.5))

    # M16 gland hole, teardrop (prints without support with the base upright)
    r = GLAND_D / 2
    tear = (cq.Workplane("XZ").center(GLAND_X, GLAND_Z).circle(r).extrude(WALL + 2)
            .union(cq.Workplane("XZ").center(GLAND_X, GLAND_Z)
                   .polyline([(-r * 0.7071, r * 0.7071), (0, r * 1.414), (r * 0.7071, r * 0.7071)]).close()
                   .extrude(WALL + 2)))
    # flat-topped teardrop: keeps >= 3 mm of wall below the lid seat
    cap = cq.Workplane("XY").box(GLAND_D + 2, WALL + 4, GLAND_D, centered=(True, True, False)) \
        .translate((GLAND_X, IN_Y1, GLAND_Z + r * 1.1 - GLAND_D))
    b = b.cut(tear.translate((0, IN_Y1 + 1, 0)).intersect(cap))

    if mount == "din":
        b = add_din_clip(b)
    elif mount == "wall":
        b = add_wall_flanges(b)
    else:
        raise ValueError(mount)
    return b


def add_din_clip(b):
    """TS35 rail clip on the floor underside: rail along X, fixed hook + spring latch."""
    y_top_edge = DIN_CY + RAIL_W / 2       # upper rail edge
    y_bot_edge = DIN_CY - RAIL_W / 2
    rib_h = 1.2                            # box rests on the rail flanges
    for y in (y_top_edge - 3.0, y_bot_edge + 3.0):
        b = b.union(cq.Workplane("XY").box(DIN_LEN, 3.0, rib_h).translate((DIN_X, y, -rib_h / 2)))
    gap = RAIL_T + 0.3
    # fixed hook: wall above the upper edge + lip under the flange
    hook_wall = cq.Workplane("XY").box(DIN_LEN, 2.5, rib_h + gap + 1.6).translate(
        (DIN_X, y_top_edge + 1.25 + 0.2, -(rib_h + gap + 1.6) / 2))
    hook_lip = cq.Workplane("XY").box(DIN_LEN, 2.0, 1.6).translate((DIN_X, y_top_edge - 0.8 + 0.2, -(rib_h + gap + 0.8)))
    b = b.union(hook_wall).union(hook_lip)
    # spring latch: cantilever along -Y anchored beyond the lower edge, barb under the flange
    arm_len, arm_t, arm_w = 16.0, 1.8, 14.0
    anchor_y = y_bot_edge - arm_len
    anchor = cq.Workplane("XY").box(arm_w, 4.0, rib_h).translate((DIN_X, anchor_y - 2.0, -rib_h / 2))
    arm = cq.Workplane("XY").box(arm_w, arm_len + 4.0, arm_t).translate(
        (DIN_X, anchor_y + (arm_len + 4.0) / 2 - 4.0, -(rib_h + arm_t / 2)))
    barb = (cq.Workplane("YZ").polyline([(y_bot_edge - 0.2, -(rib_h + arm_t)), (y_bot_edge + 1.4, -(rib_h + arm_t)),
                                          (y_bot_edge - 0.2, -(rib_h + arm_t + gap + 1.6))]).close()
            .extrude(arm_w).translate((DIN_X - arm_w / 2, 0, 0)))
    tab = cq.Workplane("XY").box(arm_w, 3.0, 4.0).translate((DIN_X, anchor_y - 1.5, -(rib_h + 2.0)))
    b = b.union(anchor).union(arm).union(barb).union(tab)
    # release slot (screwdriver) in the tab
    b = b.cut(cq.Workplane("XY").box(6.0, 1.2, 3.0).translate((DIN_X, anchor_y - 1.5, -(rib_h + 2.6))))

    return b


def add_wall_flanges(b):
    """Screw flanges at both short ends, flush with the floor, with slotted holes."""
    cy = (OUT_Y0 + OUT_Y1) / 2
    depth = OUT_Y0 - OUT_Y1
    for side in (-1, 1):
        x_edge = OUT_X0 if side < 0 else OUT_X1
        fl = cq.Workplane("XY").box(FLANGE_W + 2.0, depth * 0.6, FLANGE_T).translate(
            (x_edge + side * (FLANGE_W / 2 - 1.0), cy, FLANGE_T / 2))
        fl = fl.edges("|Z").fillet(2.0)
        b = b.union(fl)
        slot = cq.Workplane("XY").slot2D(SCREW_SLOT_LEN, SCREW_SLOT_D, 90).extrude(FLANGE_T + 2) \
            .translate((x_edge + side * (FLANGE_W / 2 + 0.5), cy, -1))
        b = b.cut(slot)
    return b


def lid():
    w, d = OUT_X1 - OUT_X0, OUT_Y0 - OUT_Y1
    plate = cq.Workplane("XY").box(w, d, LID, centered=False).translate((OUT_X0, OUT_Y1, TOP_Z))
    plate = plate.edges("|Z").fillet(1.5)
    # locating lip inside the walls, interrupted at the bosses
    lip_out = cq.Workplane("XY").box(IN_X1 - IN_X0 - 2 * FIT, IN_Y0 - IN_Y1 - 2 * FIT, 2.0, centered=False) \
        .translate((IN_X0 + FIT, IN_Y1 + FIT, TOP_Z - 2.0))
    lip_in = cq.Workplane("XY").box(IN_X1 - IN_X0 - 2 * FIT - 3.2, IN_Y0 - IN_Y1 - 2 * FIT - 3.2, 2.0, centered=False) \
        .translate((IN_X0 + FIT + 1.6, IN_Y1 + FIT + 1.6, TOP_Z - 2.0))
    lip = lip_out.cut(lip_in)
    for x, y in BOSSES:
        lip = lip.cut(cq.Workplane("XY").circle(BOSS_D / 2 + FIT).extrude(3.0).translate((x, y, TOP_Z - 2.5)))
    # no lip above the gland: the M16 lock nut (about 22-24 mm) sits there
    lip = lip.cut(cq.Workplane("XY").box(GLAND_NUT_D + 2, 6.0, 3.0).translate((GLAND_X, IN_Y1 + 2.0, TOP_Z - 1.0)))
    lid = plate.union(lip)
    # M3 screw holes, counterbored
    for x, y in BOSSES:
        lid = lid.cut(cq.Workplane("XY").circle(1.7).extrude(LID + 1).translate((x, y, TOP_Z - 0.5)))
        lid = lid.cut(cq.Workplane("XY").circle(3.1).extrude(1.3).translate((x, y, TOP_Z + LID - 1.2)))
    # LED light holes
    for x, y in LED_HOLES:
        lid = lid.cut(cq.Workplane("XY").circle(LED_HOLE_D / 2).extrude(LID + 1).translate((x, y, TOP_Z - 0.5)))
    # PAIR plunger guide
    px, py = PAIR
    guide_bottom = BUTTON_TOP + PLUNGER_TRAVEL + PLUNGER_FLANGE_T + 0.8
    guide = cq.Workplane("XY").circle(3.6).extrude(TOP_Z - guide_bottom).translate((px, py, guide_bottom))
    lid = lid.union(guide)
    lid = lid.cut(cq.Workplane("XY").circle(PLUNGER_HOLE_D / 2).extrude(TOP_Z + LID - guide_bottom + 1)
                  .translate((px, py, guide_bottom - 0.5)))
    # label
    label = (cq.Workplane("XY").workplane(offset=TOP_Z + LID - 0.6)
             .center((OUT_X0 + OUT_X1) / 2 - 18.0, OUT_Y1 + 12.0)
             .text("AccessBridge C6", 6.0, 0.6, fontPath=FONT, combine=False))
    lid = lid.cut(label)
    return lid


def plunger():
    px, py = PAIR
    z0 = BUTTON_TOP + PLUNGER_TRAVEL
    rod_len = TOP_Z + LID + 1.0 - z0           # protrudes 1 mm above the lid
    flange = cq.Workplane("XY").circle(PLUNGER_FLANGE_D / 2).extrude(PLUNGER_FLANGE_T)
    rod = cq.Workplane("XY").circle(PLUNGER_D / 2).extrude(rod_len)
    return flange.union(rod).translate((px, py, z0))


def clamp():
    (x0, y), (x1, _) = CLAMP_POSTS
    length = x1 - x0 + 10.0
    bar = cq.Workplane("XY").box(length, 8.0, 4.0).translate(((x0 + x1) / 2, y, 0))
    bar = bar.cut(cq.Workplane("XZ").center((x0 + x1) / 2, -2.0).ellipse(8.0, 2.2).extrude(5.0).translate((0, y + 2.5, 0)))
    for x in (x0, x1):
        bar = bar.cut(cq.Workplane("XY").circle(1.7).extrude(6).translate((x, y, -3)))
    # in the assembly the bar sits on the posts, cables pressed between bar and post tops
    return bar.translate((0, 0, FLOOR + CLAMP_POST_H + 2.0 + 3.0))


PARTS = {"base-din": lambda: base("din"), "base-wall": lambda: base("wall"),
         "lid": lid, "plunger": plunger, "clamp": clamp}


def build():
    return {name: fn() for name, fn in PARTS.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=HERE)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    for name, part in build().items():
        stem = os.path.join(args.out, f"accessbridge-enclosure-{name}")
        cq.exporters.export(part, stem + ".step")
        cq.exporters.export(part, stem + ".stl", tolerance=0.02, angularTolerance=0.1)
        bb = part.val().BoundingBox()
        print(f"{name:10s} {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:5.1f} mm  volume {part.val().Volume() / 1000:6.1f} cm3")


if __name__ == "__main__":
    main()
