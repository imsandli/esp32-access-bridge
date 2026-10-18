# Releases

Releases are built by [`.github/workflows/release.yml`](../.github/workflows/release.yml)
when a tag `HW-<hw>_FW-<fw>` is pushed, for example `HW-1.0_FW-1.0.0`. The
workflow:

1. checks that the tag matches `HW_VERSION` in `hardware/kicad/accessbridge.kicad_pro`
   and `fw_version` in `firmware/esphome/accessbridge.yaml`;
2. runs the hardware workflow (ERC, DRC, fabrication export, reproducibility
   check) and the firmware workflow (config, compile);
3. publishes a GitHub release with firmware binaries, the Gerber ZIP, BOMs,
   CPL, schematic PDF, dimension drawing and `SHA256SUMS`. The title and notes
   name the hardware revision and firmware version.

Release binaries are **not** committed to the repository.

## Version scheme

| Item | Format | Current |
|---|---|---|
| Hardware | `HW-MAJOR.MINOR` (electrical/footprint changes bump MINOR, incompatible pinout MAJOR) | HW-1.0 |
| PCB revision | `Rev A`, `Rev B`, ... (any change to the Gerbers) | Rev A |
| Firmware | `FW-MAJOR.MINOR.PATCH` (semantic) | FW-1.0.0 |

## Compatibility

| Firmware | Hardware | Status |
|---|---|---|
| FW-1.0.0 | HW-1.0 Rev A | statically checked, compiled, software-tested. **Not tested on hardware.** |

The authoritative test record is [docs/testing.md](../docs/testing.md).

## Published releases

None yet. The first release should be tagged only after the electrical tests
(T-EL-*) pass on a manufactured Rev A board.
