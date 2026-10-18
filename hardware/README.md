# AccessBridge C6: hardware

**HW-1.0, PCB Rev A**, KiCad 9.0.9, 2 layers, 86 x 56 mm, CERN-OHL-S-2.0.

![PCB 3D view](docs/images/pcb-iso.png)

| | |
|---|---|
| Schematic (PDF) | [docs/schematic.pdf](docs/schematic.pdf) |
| Pinout | [docs/pinout.md](docs/pinout.md) |
| Wiring (UA-Hub) | [docs/wiring.md](docs/wiring.md) |
| Power budget | [docs/power-budget.md](docs/power-budget.md) |
| Assembly / ordering | [docs/assembly.md](docs/assembly.md) |
| Fabrication data | [manufacturing/](manufacturing/README.md) |
| Enclosure | [enclosure/](enclosure/README.md) |
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
reserved for project models; none are needed for Rev A. The XIAO module itself
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
* **Revision marking:** `AccessBridge C6 HW-1.0 Rev A` on the top silkscreen
  and in the title blocks.

## Checks (KiCad CLI)

```sh
scripts/validate-hardware.sh   # ERC + DRC with --schematic-parity, fails on any violation
scripts/export-bom.sh          # full BOM, JLCPCB BOM/CPL, manual assembly list
scripts/export-gerbers.sh      # Gerbers, drill, ZIP, schematic PDF, drawings, 3D renders
```

The scripts use a native KiCad 9 if available, otherwise the pinned Docker
image `kicad/kicad:9.0.9`. The raw commands they wrap are, for example:

```sh
kicad-cli sch erc --severity-all --exit-code-violations hardware/kicad/accessbridge.kicad_sch
kicad-cli pcb drc --severity-all --schematic-parity --exit-code-violations hardware/kicad/accessbridge.kicad_pcb
```

## How Rev A was created

The schematic and the initial layout were generated from
[`tools/design.py`](tools/design.py) by the scripts in [`tools/`](tools/README.md)
and routed with Freerouting. From now on, edit the KiCad files directly.
The generators are kept for transparency only.
