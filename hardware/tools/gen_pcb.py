#!/usr/bin/env python3
"""Bootstrap generator for hardware/kicad/accessbridge.kicad_pcb.

Runs inside the KiCad 9 container (needs the pcbnew Python module):
  gen_pcb.py place <netlist.net> <out.kicad_pcb>   footprints, nets, outline, texts
  gen_pcb.py update <netlist.net> <board>          incremental revision: add/move parts, keep routing
  gen_pcb.py dsn|ses <board> <file>                Specctra export / import (Freerouting)
  gen_pcb.py clean <board>                         remove dangling autorouter stubs
  gen_pcb.py shift <board>                         move board to design.SHEET_ORIGIN, set aux origin
  gen_pcb.py finish <board>                        dimensions, GND pours, antenna no-pour area, fill

Routing between the two steps is done with Freerouting via Specctra DSN/SES
(see route_pcb.sh). After bootstrap the .kicad_pcb file is edited in KiCad.
"""

import os
import sys

import pcbnew

sys.path.insert(0, os.path.dirname(__file__))
import design  # noqa: E402
from sexpr import find, find_all, parse  # noqa: E402

FPROOT = os.environ.get("KICAD9_FOOTPRINT_DIR", "/usr/share/kicad/footprints")
PROJFP = os.path.join(os.path.dirname(__file__), "..", "kicad", "footprints")
MM = pcbnew.FromMM


_origin = [0.0, 0.0]  # placement/routing happen at (0, 0); "shift" moves the board onto the sheet


def v(x, y):
    """Board-relative design coordinates -> board/sheet coordinates."""
    return pcbnew.VECTOR2I(MM(x + _origin[0]), MM(y + _origin[1]))


def load_fp(lib_id):
    lib, name = lib_id.split(":")
    base = PROJFP if lib == "AccessBridge" else FPROOT
    fp = pcbnew.FootprintLoad(os.path.join(base, lib + ".pretty"), name)
    if fp is None:
        raise SystemExit(f"footprint not found: {lib_id}")
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    return fp


def add_text(board, text, x, y, size, rot, layer):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text)
    t.SetPosition(v(x, y))
    t.SetLayer({"F.SilkS": pcbnew.F_SilkS, "B.SilkS": pcbnew.B_SilkS}[layer])
    t.SetTextSize(pcbnew.VECTOR2I(MM(size), MM(size)))
    t.SetTextThickness(MM(max(0.12, size * 0.15)))
    t.SetTextAngleDegrees(rot)
    if layer.startswith("B."):
        t.SetMirrored(True)
    board.Add(t)


def make_footprint(comp):
    """Footprint for a netlist component, placed at design.PCB_POS."""
    ref = str(find(comp, "ref")[1])
    fpid = str(find(comp, "footprint")[1])
    fp = load_fp(fpid)
    fp.SetReference(ref)
    fp.SetValue(str(find(comp, "value")[1]))
    fp.SetPath(pcbnew.KIID_PATH("/" + str(find(comp, "tstamps")[1])))
    x, y, rot = design.PCB_POS[ref]
    fp.SetPosition(v(x, y))
    fp.SetOrientationDegrees(rot)
    props = {str(find(p, "name")[1]): str(find(p, "value")[1]) for p in find_all(comp, "property")
             if find(p, "value") is not None}
    for k in ("LCSC", "MPN", "Manufacturer"):
        if props.get(k):
            fp.SetField(k, props[k])
            f = fp.GetFieldByName(k)
            f.SetVisible(False)
            f.SetLayer(pcbnew.F_Fab)
    if design.C[ref]["dnp"]:
        fp.SetDNP(True)
        fp.SetExcludedFromPosFiles(True)
    # reference designators live on the assembly (Fab) layer; silk keeps only
    # connector/function labels so nothing is printed over pads
    fp.Reference().SetLayer(pcbnew.F_Fab)
    return fp


def assign_nets(fp, pin_net):
    """Set pad nets from the netlist; return the pads whose net changed."""
    changed = []
    for pad in fp.Pads():
        ni = pin_net.get((fp.GetReference(), pad.GetNumber()))
        if ni is not None and pad.GetNetname() != ni.GetNetname():
            changed.append(pad)
            pad.SetNet(ni)
    return changed


def read_netlist(board, netfile):
    """Create missing nets on the board; return (netlist, {(ref, pin): NETINFO})."""
    net = parse(open(netfile).read())
    pin_net = {}
    for n in find_all(find(net, "nets"), "net"):
        name = str(find(n, "name")[1])
        ni = board.FindNet(name)
        if ni is None:
            ni = pcbnew.NETINFO_ITEM(board, name)
            board.Add(ni)
        for nd in find_all(n, "node"):
            pin_net[(str(find(nd, "ref")[1]), str(find(nd, "pin")[1]))] = ni
    return net, pin_net


def draw_outline(board):
    """Board outline with 1 mm corner radius."""
    w, h, r = design.BOARD_W, design.BOARD_H, 1.0
    segs = [((r, 0), (w - r, 0)), ((w, r), (w, h - r)), ((w - r, h), (r, h)), ((0, h - r), (0, r))]
    for a, b in segs:
        s = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(v(*a))
        s.SetEnd(v(*b))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(MM(0.1))
        board.Add(s)
    k = 1 - 0.5 ** 0.5
    corners = (((0, r), (r * k, r * k), (r, 0)), ((w - r, 0), (w - r * k, r * k), (w, r)),
               ((w, h - r), (w - r * k, h - r * k), (w - r, h)), ((r, h), (r * k, h - r * k), (0, h - r)))
    for st, mid, en in corners:
        a = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_ARC)
        a.SetArcGeometry(v(*st), v(*mid), v(*en))
        a.SetLayer(pcbnew.Edge_Cuts)
        a.SetWidth(MM(0.1))
        board.Add(a)


def set_title_block(board):
    tb = board.GetTitleBlock()
    tb.SetTitle(design.TITLE)
    tb.SetRevision(f"{design.PCB_REV} ({design.HW_VERSION})")
    tb.SetDate(design.DATE)
    tb.SetCompany("AccessBridge project")
    tb.SetComment(0, "License: CERN-OHL-S-2.0")


def place(netfile, out):
    board = pcbnew.NewBoard(out)
    net, pin_net = read_netlist(board, netfile)

    for comp in find_all(find(net, "components"), "comp"):
        fp = make_footprint(comp)
        board.Add(fp)
        assign_nets(fp, pin_net)

    draw_outline(board)

    for text, x, y, size, rot, layer in design.SILK:
        add_text(board, text, x, y, size, rot, layer)

    set_title_block(board)

    x1, y1, x2, y2 = design.ANTENNA_KEEPOUT
    zone(board, pcbnew.F_Cu, [(x1, y1), (x2, y1), (x2, y2), (x1, y2)], "Antenna keep-out", keepout=True)

    ds = board.GetDesignSettings()
    ds.SetCopperLayerCount(2)
    ds.SetBoardThickness(MM(1.6))
    board.Save(out)


def zone(board, layer, pts, name, net=None, keepout=False):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    if keepout:
        z.SetIsRuleArea(True)
        z.SetDoNotAllowTracks(True)
        z.SetDoNotAllowVias(True)
        z.SetDoNotAllowCopperPour(True)
        z.SetDoNotAllowPads(False)
        z.SetDoNotAllowFootprints(False)
        ls = pcbnew.LSET()
        ls.AddLayer(pcbnew.F_Cu)
        ls.AddLayer(pcbnew.B_Cu)
        z.SetLayerSet(ls)
    else:
        z.SetNet(net)
        z.SetLocalClearance(MM(0.3))
        z.SetMinThickness(MM(0.25))
        z.SetThermalReliefGap(MM(0.4))
        z.SetThermalReliefSpokeWidth(MM(0.4))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    z.SetZoneName(name)
    ol = z.Outline()
    ol.NewOutline()
    for x, y in pts:
        p = v(x, y)
        ol.Append(p.x, p.y)
    board.Add(z)
    return z


def remove_dangling(board):
    """Delete track stubs and vias left by the autorouter that end on nothing (one pass)."""
    board.BuildConnectivity()
    conn = board.GetConnectivity()
    stubs = [t for t in board.GetTracks()
             if t.Type() in (pcbnew.PCB_TRACE_T, pcbnew.PCB_VIA_T) and conn.TestTrackEndpointDangling(t, False)]
    for t in stubs:
        board.Remove(t)
    return len(stubs)


def clean(path):
    board = pcbnew.LoadBoard(path)
    print(f"removed {remove_dangling(board)} dangling track stubs")
    board.Save(path)


def dim(board, a, b, height, text_size=1.0):
    d = pcbnew.PCB_DIM_ALIGNED(board, pcbnew.PCB_DIM_ALIGNED_T)
    d.SetLayer(pcbnew.Dwgs_User)
    d.SetStart(v(*a))
    d.SetEnd(v(*b))
    d.SetHeight(MM(height))
    d.SetUnits(pcbnew.EDA_UNITS_MM)
    d.SetPrecision(pcbnew.DIM_PRECISION_X_XX)
    d.SetTextSize(pcbnew.VECTOR2I(MM(text_size), MM(text_size)))
    d.SetLineThickness(MM(0.1))
    board.Add(d)


def drawing_note(board, text, x, y, size=1.0):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text)
    t.SetPosition(v(x, y))
    t.SetLayer(pcbnew.Dwgs_User)
    t.SetTextSize(pcbnew.VECTOR2I(MM(size), MM(size)))
    t.SetTextThickness(MM(0.15))
    t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
    board.Add(t)


def add_dimensions(board):
    """Mechanical drawing annotations on Dwgs.User (not fabricated)."""
    w, h = design.BOARD_W, design.BOARD_H
    dim(board, (0, 0), (w, 0), -6)
    dim(board, (0, 0), (0, h), 6)
    (hx1, hy1), (hx2, hy2) = design.PCB_POS["H1"][:2], design.PCB_POS["H4"][:2]
    dim(board, (hx1, hy2), (hx2, hy2), 8)
    dim(board, (hx2, hy1), (hx2, hy2), -8)
    ux = design.PCB_POS["U2"][0]
    dim(board, (0, 0), (ux, 0), -12)
    drawing_note(board, f"Board {w:g} x {h:g} mm, 1.6 mm FR-4, 2 layers, 1 mm corner radius", 0, h + 12)
    drawing_note(board, "4x M3 mounting holes, 3.2 mm drill, 4 mm from board edges", 0, h + 14)
    drawing_note(board, "USB-C (XIAO) faces the top edge: connector face ~1.45 mm inside the edge, centred on X=68 mm", 0, h + 16)
    drawing_note(board, "Wire entry of J1/J2/J4 faces the bottom edge (5.08 mm pitch screw terminals)", 0, h + 18)
    drawing_note(board, "Hatched area below the XIAO: no copper (antenna keep-out)", 0, h + 20)


def shift(path):
    """Move the routed board onto the drawing sheet (design.SHEET_ORIGIN) and put the
    drill/place (aux) origin on the board's top-left corner."""
    board = pcbnew.LoadBoard(path)
    off = pcbnew.VECTOR2I(MM(design.SHEET_ORIGIN[0]), MM(design.SHEET_ORIGIN[1]))
    for item in list(board.GetFootprints()) + list(board.GetTracks()) + list(board.GetDrawings()) + list(board.Zones()):
        item.Move(off)
    ds = board.GetDesignSettings()
    ds.SetAuxOrigin(off)
    ds.SetGridOrigin(off)
    board.Save(path)


def pad_box(pad):
    bb = pad.GetBoundingBox()
    bb.Inflate(MM(0.25))
    return bb


def update(netfile, path):
    """Incremental change of an existing, routed board (Rev A -> Rev B).

    Keeps every existing footprint position and track. Adds footprints that are
    new in the netlist, moves footprints whose design.PCB_POS changed, applies
    net changes, and removes only the tracks that touch a pad with a changed
    net or overlap a new/moved footprint. The remaining tracks are locked, so
    Freerouting (Specctra "protect") routes only the missing connections.
    """
    _origin[:] = design.SHEET_ORIGIN
    board = pcbnew.LoadBoard(path)
    # collect every item list before modifying the board: iterating Zones() or
    # Tracks() after a Remove() crashes the KiCad 9 SWIG bindings
    tracks = list(board.GetTracks())
    zones = list(board.Zones())
    drawings = list(board.GetDrawings())
    net, pin_net = read_netlist(board, netfile)
    existing = {fp.GetReference(): fp for fp in board.GetFootprints()}
    changed_pads, touched = [], []
    for comp in find_all(find(net, "components"), "comp"):
        ref = str(find(comp, "ref")[1])
        fp = existing.get(ref)
        if fp is None:
            fp = make_footprint(comp)
            board.Add(fp)
            touched.append(fp)
            print(f"added {ref}")
        else:
            x, y, rot = design.PCB_POS[ref]
            if fp.GetPosition() != v(x, y) or abs(fp.GetOrientationDegrees() - rot) > 0.01:
                fp.SetPosition(v(x, y))
                fp.SetOrientationDegrees(rot)
                touched.append(fp)
                print(f"moved {ref}")
        for pad in assign_nets(fp, pin_net):
            changed_pads.append(pad)
            print(f"net change {ref}.{pad.GetNumber()} -> {pad.GetNetname()}")

    boxes = []
    for fp in touched:
        bb = fp.GetCourtyard(pcbnew.F_CrtYd).BBox() if fp.GetCourtyard(pcbnew.F_CrtYd).OutlineCount() else fp.GetBoundingBox()
        bb.Inflate(MM(0.4))
        boxes.append(bb)
    removed = 0
    kept = []
    for t in tracks:
        pts = [t.GetPosition()] if t.Type() == pcbnew.PCB_VIA_T else [t.GetStart(), t.GetEnd()]
        hit = any(pad.HitTest(p) for pad in changed_pads for p in pts)
        # also tracks of another net that merely pass over/into a re-netted pad
        hit = hit or any(t.GetNetname() != pad.GetNetname() and pad_box(pad).Intersects(t.GetBoundingBox())
                         for pad in changed_pads)
        hit = hit or any(bb.Intersects(t.GetBoundingBox()) for bb in boxes)
        if hit:
            board.Remove(t)
            removed += 1
        else:
            kept.append(t)
    print(f"removed {removed} affected tracks/vias")

    # outline, silkscreen texts, drawing annotations and copper pours are
    # regenerated from design.py (finish adds pours + dimensions again)
    for d in drawings:
        if d.GetLayer() in (pcbnew.Edge_Cuts, pcbnew.Dwgs_User) or (
                d.Type() == pcbnew.PCB_TEXT_T and d.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS)):
            board.Remove(d)
    draw_outline(board)
    for text, x, y, size, rot, layer in design.SILK:
        add_text(board, text, x, y, size, rot, layer)
    for z in zones:
        if not z.GetIsRuleArea() or z.GetZoneName() == "Antenna end: no pour":
            board.Remove(z)
    set_title_block(board)
    for t in kept:
        t.SetLocked(True)
    board.Save(path)


def lock(path):
    board = pcbnew.LoadBoard(path)
    for t in board.GetTracks():
        t.SetLocked(True)
    board.Save(path)


def finish(path):
    _origin[:] = design.SHEET_ORIGIN
    board = pcbnew.LoadBoard(path)
    for t in board.GetTracks():
        t.SetLocked(False)
    add_dimensions(board)
    for z in list(board.Zones()):
        if not z.GetIsRuleArea():
            board.Remove(z)
    gnd = board.FindNet("GND")
    w, h, m = design.BOARD_W, design.BOARD_H, 0.0
    outline = [(m, m), (w - m, m), (w - m, h - m), (m, h - m)]
    zone(board, pcbnew.F_Cu, outline, "GND top", gnd)
    zone(board, pcbnew.B_Cu, outline, "GND bottom", gnd)
    # no copper pour under the XIAO antenna end (tracks to pins D6/D7 stay allowed)
    x1, y1, x2, y2 = design.ANTENNA_NO_POUR
    nopour = zone(board, pcbnew.F_Cu, [(x1, y1), (x2, y1), (x2, y2), (x1, y2)], "Antenna end: no pour", keepout=True)
    nopour.SetDoNotAllowTracks(False)
    nopour.SetDoNotAllowVias(False)
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    board.Save(path)


def dsn(path, out):
    board = pcbnew.LoadBoard(path)
    if not pcbnew.ExportSpecctraDSN(board, out):
        raise SystemExit("DSN export failed")


def ses(path, sesfile):
    board = pcbnew.LoadBoard(path)
    if not pcbnew.ImportSpecctraSES(board, sesfile):
        raise SystemExit("SES import failed")
    board.Save(path)


if __name__ == "__main__":
    if sys.argv[1] == "place":
        place(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "update":
        update(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "dsn":
        dsn(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "ses":
        ses(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "clean":
        clean(sys.argv[2])
    elif sys.argv[1] == "shift":
        shift(sys.argv[2])
    elif sys.argv[1] == "lock":
        lock(sys.argv[2])
    elif sys.argv[1] == "finish":
        finish(sys.argv[2])
    else:
        raise SystemExit(__doc__)
