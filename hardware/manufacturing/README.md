# Fabrication data: AccessBridge C6 HW-1.0 Rev A

**Generated files. Do not edit by hand.** They are produced from
`hardware/kicad/` by:

```sh
scripts/export-bom.sh
scripts/export-gerbers.sh
```

CI (`.github/workflows/hardware.yml`) regenerates them on every change and
fails if the committed files differ from the sources (ignoring timestamps).
Tagged releases attach the same files.

| Path | Content |
|---|---|
| `accessbridge-c6-HW-1.0-revA-gerbers.zip` | **Upload to JLCPCB.** Gerbers + Excellon drill, flat ZIP, deterministic |
| `gerber/` | Gerber X2, Protel extensions: F/B Cu, Mask, Paste, Silkscreen, Edge.Cuts, job file |
| `drill/` | Excellon (mm, plated and non-plated in one file), drill map PDF |
| `bom/accessbridge-bom-full.csv` | All parts: manufacturer, MPN, LCSC, sourcing status |
| `bom/accessbridge-jlcpcb-bom.csv` | JLCPCB BOM (Comment, Designator, Footprint, LCSC Part #, Note) |
| `bom/accessbridge-manual-assembly.csv` | Through-hole parts to solder by hand (terminals, XIAO sockets) |
| `pick-and-place/accessbridge-jlcpcb-cpl.csv` | JLCPCB CPL (Designator, Mid X, Mid Y, Layer, Rotation), top side, origin = board corner |

Coordinates of Gerbers, drill and CPL all use the drill/place origin at the
board's top-left corner.

## Specification

| Parameter | Value |
|---|---|
| Layers | 2 |
| Material | FR-4, 1.6 mm, 1 oz Cu |
| Size | 86.0 x 56.0 mm, 1 mm corner radius |
| Min. track / clearance | 0.25 / 0.2 mm (JLCPCB standard capability) |
| Min. drill | 0.3 mm vias, 1.0 mm socket pins, 1.3 mm terminals, 3.2 mm NPTH mounting holes |
| Assembly | SMT top side only, plus THT terminals and sockets (manual or JLCPCB THT) |

## Sourcing status of LCSC numbers

Taken from the `LCSC status` column of the full BOM:

* **confirmed**: the part number was seen on an LCSC/JLCPCB part page during
  design (2026-10).
* **secondary**: the part number comes from a third-party JLCPCB basic-parts
  list. Verify value/voltage when ordering.
* **unverified**: no number found (R8, 470 Ω 0603). Select at order time.
* **manual**: not machine assembled.

Stock and prices were **not** checked live: LCSC/JLCPCB were not reachable
from the design environment. Check availability before ordering.
