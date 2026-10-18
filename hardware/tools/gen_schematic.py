#!/usr/bin/env python3
"""Bootstrap generator for hardware/kicad/accessbridge.kicad_sch.

Usage: gen_schematic.py <kicad_symbol_dir> <out.kicad_sch>

Every pin gets a short wire stub that ends in a local label or a KiCad power
symbol, so connectivity is explicit and checkable by ERC. After bootstrap the
schematic is edited in KiCad directly.
"""

import copy
import math
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(__file__))
import design  # noqa: E402
from sexpr import QStr, dumps, find, find_all, parse  # noqa: E402

SYMDIR = sys.argv[1]
OUT = sys.argv[2]
PROJLIB = os.path.join(os.path.dirname(__file__), "..", "kicad", "symbols", "AccessBridge.kicad_sym")

_ns = uuid.UUID("6f1b8f1e-0c2a-4d7e-9a51-acce55b41d6e")


def U(key):
    return QStr(str(uuid.uuid5(_ns, key)))


ROOT = U("root-sheet")
_libs = {}


def lib_file(lib):
    if lib == "AccessBridge":
        return PROJLIB
    return os.path.join(SYMDIR, lib + ".kicad_sym")


def raw_symbol(lib, name):
    if lib not in _libs:
        _libs[lib] = parse(open(lib_file(lib)).read())
    for s in find_all(_libs[lib], "symbol"):
        if s[1] == name:
            return s
    raise KeyError(f"{lib}:{name}")


def flat_symbol(lib_id):
    lib, name = lib_id.split(":")
    s = raw_symbol(lib, name)
    ext = find(s, "extends")
    if not ext:
        out = copy.deepcopy(s)
    else:
        # derived symbol: parent graphics/pins + child properties
        out = copy.deepcopy(flat_symbol(f"{lib}:{ext[1]}"))
        child_props = {p[1]: p for p in find_all(s, "property")}
        out = [x for x in out if not (isinstance(x, list) and x[0] == "property" and x[1] in child_props)]
        idx = min(i for i, x in enumerate(out) if isinstance(x, list) and x[0] == "symbol")
        out[idx:idx] = [copy.deepcopy(p) for p in child_props.values()]
    # sub-units are named "<symbol>_<unit>_<style>" without library prefix
    for sub in find_all(out, "symbol"):
        _, unit, style = sub[1].rsplit("_", 2)
        sub[1] = QStr(f"{name}_{unit}_{style}")
    out = [x for x in out if not (isinstance(x, list) and x[0] == "extends")]
    out[1] = QStr(lib_id)
    return out


def symbol_pins(sym):
    pins = []
    for sub in find_all(sym, "symbol"):
        for p in find_all(sub, "pin"):
            at = find(p, "at")
            num = find(p, "number")[1]
            name = find(p, "name")[1]
            pins.append(dict(num=str(num), name=str(name), x=float(at[1]), y=float(at[2]), a=float(at[3]), etype=p[1]))
    return pins


def xform(sx, sy, px, py, rot):
    a = math.radians(rot)
    rx = px * math.cos(a) - py * math.sin(a)
    ry = px * math.sin(a) + py * math.cos(a)
    return round(sx + rx, 4), round(sy - ry, 4)


def outward(pin_angle, rot):
    return (pin_angle + 180 + rot) % 360


def font(size=1.27, bold=False, hide=False, justify=None):
    e = ["effects", ["font", ["size", size, size]] + ([["bold", "yes"]] if bold else [])]
    if justify:
        e.append(["justify"] + justify)
    if hide:
        e.append(["hide", "yes"])
    return e


lib_symbols = {}
items = []
pwr_count = [0]


def use(lib_id):
    if lib_id not in lib_symbols:
        lib_symbols[lib_id] = flat_symbol(lib_id)
    return lib_symbols[lib_id]


def instance(ref, lib_id, x, y, rot, props, pins, dnp=False, in_bom=True, on_board=True, key=None):
    sym = use(lib_id)
    key = key or ref
    node = ["symbol", ["lib_id", QStr(lib_id)], ["at", x, y, rot], ["unit", 1],
            ["exclude_from_sim", "no"], ["in_bom", "yes" if in_bom else "no"],
            ["on_board", "yes" if on_board else "no"], ["dnp", "yes" if dnp else "no"],
            ["uuid", U("sym-" + key)]]
    libprops = {p[1]: p for p in find_all(sym, "property")}
    for k, v, hide in props:
        lp = libprops.get(k)
        if lp is not None:
            at = find(lp, "at")
            px, py = xform(x, y, float(at[1]), float(at[2]), rot)
            ang = (float(at[3]) + rot) % 180
            just = None
            eff = find(lp, "effects")
            j = find(eff, "justify") if eff else None
            if j and rot == 0:
                just = [str(t) for t in j[1:]]
        else:
            px, py, ang, just = x, y, 0, None
        node.append(["property", QStr(k), QStr(v), ["at", px, py, ang], font(hide=hide, justify=just)])
    for p in symbol_pins(sym):
        node.append(["pin", QStr(p["num"]), ["uuid", U(f"pin-{key}-{p['num']}")]])
    node.append(["instances", ["project", QStr(design.PROJECT),
                               ["path", QStr("/" + ROOT), ["reference", QStr(ref)], ["unit", 1]]]])
    items.append(node)
    return sym


def wire(x1, y1, x2, y2, key):
    items.append(["wire", ["pts", ["xy", x1, y1], ["xy", x2, y2]], ["stroke", ["width", 0], ["type", "default"]], ["uuid", U(key)]])


def label(net, x, y, ang, key):
    just = {0: ["left", "bottom"], 90: ["left", "bottom"], 180: ["right", "bottom"], 270: ["right", "bottom"]}[int(ang)]
    items.append(["label", QStr(net), ["at", x, y, ang], ["fields_autoplaced", "yes"], font(justify=just), ["uuid", U(key)]])


def power_symbol(net, x, y, direction, key):
    lib_id = design.POWER_SYMBOLS[net]
    sym = use(lib_id)
    pin = symbol_pins(sym)[0]
    rot = (direction - (pin["a"] + 180)) % 360
    pwr_count[0] += 1
    ref = f"#PWR{pwr_count[0]:03d}"
    instance(ref, lib_id, x, y, rot, [("Reference", ref, True), ("Value", net, False),
                                      ("Footprint", "", True), ("Datasheet", "", True)],
             None, in_bom=False, on_board=True, key=key)


def connect(ref, pin, net, x, y, direction):
    length = 5.08 if net in design.POWER_SYMBOLS and direction in (0, 180) else 2.54
    dx = round(math.cos(math.radians(direction)) * length, 4)
    dy = round(-math.sin(math.radians(direction)) * length, 4)
    ex, ey = round(x + dx, 4), round(y + dy, 4)
    wire(x, y, ex, ey, f"w-{ref}-{pin}")
    if net in design.POWER_SYMBOLS:
        power_symbol(net, ex, ey, direction, f"p-{ref}-{pin}")
    else:
        label(net, ex, ey, direction if direction in (0, 90, 180, 270) else 0, f"l-{ref}-{pin}")


def check_overlaps():
    """Fail if a wire end touches another wire of a different net (accidental short)."""
    segs = []
    for it in items:
        if it[0] == "wire":
            p = find(it, "pts")
            segs.append(((float(p[1][1]), float(p[1][2])), (float(p[2][1]), float(p[2][2])), str(find(it, "uuid")[1])))
    ends = {}
    for a, b, k in segs:
        for p in (a, b):
            ends.setdefault(p, []).append(k)

    def on(p, a, b):
        (x, y), (x1, y1), (x2, y2) = p, a, b
        if abs((x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)) > 1e-6:
            return False
        return min(x1, x2) - 1e-6 <= x <= max(x1, x2) + 1e-6 and min(y1, y2) - 1e-6 <= y <= max(y1, y2) + 1e-6

    bad = [p for p, ks in ends.items() if len(ks) > 1]
    bad += [p for p in ends for a, b, _ in segs if p not in (a, b) and on(p, a, b)]
    if bad:
        raise SystemExit(f"schematic wire collisions at {sorted(set(bad))}")


def main():
    for ref, c in sorted(design.C.items()):
        lib_id, value, fp, mfr, mpn, lcsc, status = design.P[c["part"]]
        value = c["value"] or value
        x, y, rot = c["sch"]
        props = [("Reference", ref, False), ("Value", value, False), ("Footprint", fp, True),
                 ("Datasheet", "", True), ("MPN", mpn, True), ("Manufacturer", mfr, True),
                 ("LCSC", lcsc, True), ("LCSC_Status", status, True)]
        if c["note"]:
            props.append(("Note", c["note"], True))
        sym = instance(ref, lib_id, x, y, rot, props, c["pins"], dnp=c["dnp"],
                       in_bom=c["part"] not in ("MH", "SJ3", "SJ2"))
        stacked = {}  # pins at the same position (e.g. USB-C VBUS A9/B9) get one stub
        for p in symbol_pins(sym):
            net = c["pins"].get(p["num"])
            if net is None:
                raise SystemExit(f"{ref} pin {p['num']} unassigned")
            px, py = xform(x, y, p["x"], p["y"], rot)
            if (px, py) in stacked:
                if stacked[(px, py)] != net:
                    raise SystemExit(f"{ref}: stacked pins at {px},{py} on different nets")
                continue
            stacked[(px, py)] = net
            connect(ref, p["num"], net, px, py, outward(p["a"], rot))
        extra = set(c["pins"]) - {p["num"] for p in symbol_pins(sym)}
        if extra:
            raise SystemExit(f"{ref}: unknown pins {extra}")

    for i, (net, (x, y)) in enumerate(sorted(design.PWR_FLAGS.items()), start=1):
        ref = f"#FLG{i:02d}"
        instance(ref, "power:PWR_FLAG", x, y, 0, [("Reference", ref, True), ("Value", "PWR_FLAG", True),
                                                   ("Footprint", "", True), ("Datasheet", "", True)],
                 None, in_bom=False, on_board=True, key="flag-" + net)
        connect(ref, "1", net, x, y, 270)

    for title, x1, y1, x2, y2 in design.FRAMES:
        items.append(["rectangle", ["start", x1, y1], ["end", x2, y2],
                      ["stroke", ["width", 0.3], ["type", "dash"]], ["fill", ["type", "none"]], ["uuid", U("frame-" + title)]])
        items.append(["text", QStr(title), ["exclude_from_sim", "no"], ["at", x1 + 1.27, y1 + 2.54, 0],
                      font(size=2.0, bold=True, justify=["left", "bottom"]), ["uuid", U("ftext-" + title)]])
    for (x, y), t in design.NOTES:
        items.append(["text", QStr(t), ["exclude_from_sim", "no"], ["at", x, y, 0],
                      font(size=1.27, justify=["left", "bottom"]), ["uuid", U("note-" + t)]])

    check_overlaps()
    sch = ["kicad_sch", ["version", 20250114], ["generator", QStr("eeschema")], ["generator_version", QStr("9.0")],
           ["uuid", ROOT], ["paper", QStr("A3")],
           ["title_block", ["title", QStr(design.TITLE)], ["date", QStr(design.DATE)],
            ["rev", QStr(f"{design.PCB_REV} ({design.HW_VERSION})")], ["company", QStr("AccessBridge project")],
            ["comment", 1, QStr("Zigbee dry-contact bridge for UniFi Access UA-Hub, Seeed XIAO ESP32C6")],
            ["comment", 2, QStr("License: CERN-OHL-S-2.0")]],
           ["lib_symbols"] + [lib_symbols[k] for k in sorted(lib_symbols)]]
    sch += items
    sch += [["sheet_instances", ["path", QStr("/"), ["page", QStr("1")]]], ["embedded_fonts", "no"]]
    with open(OUT, "w") as f:
        f.write(dumps(sch) + "\n")


if __name__ == "__main__":
    main()
