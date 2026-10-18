# AccessBridge C6: hardware

**HW-1.1, PCB Rev B**, KiCad 9.0.9, 2 layers, 96 x 56 mm, CERN-OHL-S-2.0.

Rev B = Rev A plus a **USB-C power input** (J6, 5 V, power only) in a 10 mm
wider right-hand strip. All Rev A parts kept their positions, and Rev A
tracks were kept except around the rewired loop resistors (R10/R14/R18 now on
`V_LOOP`) and R18's neighbourhood.

![PCB 3D view](docs/images/pcb-iso.png)

| | |
|---|---|
| Schematic (PDF) | [docs/schematic.pdf](docs/schematic.pdf) |
| Pinout | [docs/pinout.md](docs/pinout.md) |
| Wiring (UA-Hub) | [docs/wiring.md](docs/wiring.md) |
| Power budget | [docs/power-budget.md](docs/power-budget.md) |
| Assembly / ordering | [docs/assembly.md](docs/assembly.md) |
| Fabrication data | [manufacturing/](manufacturing/README.md) |
| Enclosure (3D print, DIN or wall variant) | [enclosure/](enclosure/README.md) |
| Dimension drawing | [enclosure/drawings/accessbridge-c6-dimensions.pdf](enclosure/drawings/accessbridge-c6-dimensions.pdf) |

## Status

| Check | Status |
|---|---|
| ERC (KiCad 9.0.9, all severities) | **0 errors, 0 warnings** (local and CI) |
| DRC incl. schematic parity (all severities) | **0 violations, 0 unconnected, 0 parity issues** (local and CI) |
| Fabrication data reproducible from sources | **yes**, checked in CI (`scripts/tools/check_generated.py`) |
| Prototype manufactured | no |
| Electrically tested | **no** |

## Source files (`kicad/`)

| File | Content |
|---|---|
| `accessbridge.kicad_pro` | Project: design rules (JLCPCB-safe: 0.2 mm clearance/track, 0.3 mm drill), net classes (Power 0.5 mm, Field 0.3 mm clearance), text variables `HW_VERSION`, `PCB_REV` |
| `accessbridge.kicad_sch` | Schematic (single A3 sheet, framed blocks: connectors, power, MCU, contact inputs, DPS port, output) |
| `accessbridge.kicad_pcb` | Layout |
| `symbols/AccessBridge.kicad_sym` | `XIAO_ESP32C6` symbol (pin names = XIAO D-pin / GPIO) |
| `footprints/AccessBridge.pretty/` | `XIAO_ESP32C6_Socketed` (pad geometry from the Seeed OPL library, 3D = 2x KiCad PinSocket_1x07; includes the antenna keep-out between the pin rows) |
| `sym-lib-table`, `fp-lib-table` | Project libraries via `${KIPRJMOD}` (relative paths) |

All other symbols, footprints and 3D models come from the KiCad 9 standard
libraries (`kicad/kicad:9.0.9-full` contains the 3D models). `3dmodels/` is
reserved for project models; none are needed. The XIAO module itself
has no 3D model: only its sockets are shown.

## Design notes

* **Antenna:** the XIAO's ceramic antenna end (opposite USB-C) has no copper
  between the pin rows, no copper pour below the module end, and a 9 mm
  copper keep-out beyond the module edge on both layers. The module sits about
  8.5 mm above the carrier on its sockets. The exact antenna position on the
  module should be confirmed with a physical sample (open point).
* **Contact inputs:** see [docs/architecture.md](../docs/architecture.md),
  decision A4, and the isolation assessment.
* **Reference designators** are on the Fab layer (assembly drawing
  `docs/assembly-top.pdf`). The silkscreen carries only functional labels,
  so nothing is printed on pads.
* **USB-C power (J6):** VBUS -> PTC F2 (500 mA) + TVS D14 -> D13 into `+5V_XIAO`
  (diode-OR with D3 from the buck) and D16 into `V_LOOP` (diode-OR with D15 from
  +12 V), so the contact inputs also work on USB. CC1/CC2 have 5.1 kΩ to GND
  (USB-C sink). J4 OUT+ stays 12 V only. There is no USB data: the XIAO does not
  route D+/D- to its pins, so firmware goes through the XIAO's own USB-C, which
  sits 15 mm from J6 on the same board edge.
* **Revision marking:** `AccessBridge C6 HW-1.1 Rev B` on the top silkscreen
  and in the title blocks.

## Checks (KiCad CLI)

```sh
scripts/validate-hardware.sh   # ERC + DRC with --schematic-parity, fails on any violation
scripts/export-bom.sh          # full BOM, JLCPCB BOM/CPL, manual assembly list
scripts/export-gerbers.sh      # Gerbers, drill, ZIP, schematic PDF, drawings, 3D renders, PCB STEP
scripts/export-enclosure.sh    # 3D-printed enclosure: STEP/STL, previews, fit check (CadQuery)
```

The scripts use a native KiCad 9 if available, otherwise the pinned Docker
image `kicad/kicad:9.0.9`. The raw commands they wrap are, for example:

```sh
kicad-cli sch erc --severity-all --exit-code-violations hardware/kicad/accessbridge.kicad_sch
kicad-cli pcb drc --severity-all --schematic-parity --exit-code-violations hardware/kicad/accessbridge.kicad_pcb
```

## How Rev A and Rev B were created

Rev A's schematic and initial layout were generated from
[`tools/design.py`](tools/design.py) by the scripts in [`tools/`](tools/README.md)
and routed with Freerouting. Rev B was an incremental change of that board
(`gen_pcb.py update`, then only the new connections routed). From now on, edit
the KiCad files directly.
The generators are kept for transparency only.
