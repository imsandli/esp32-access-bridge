# Contributing

Thanks for helping! AccessBridge is part of a door access chain, so
correctness and honesty about test status matter more than features.

## Ground rules

* **Never claim a test level that was not reached.** Use the levels in
  [docs/testing.md](docs/testing.md) and record results there.
* Do not commit secrets (`firmware/esphome/secrets.yaml` is git-ignored).
* Hardware changes keep schematic and PCB consistent: `scripts/validate-hardware.sh`
  must pass, which runs ERC, and DRC with schematic parity, failing on any violation.
* Regenerate and commit fabrication data after hardware changes:
  `scripts/export-bom.sh && scripts/export-gerbers.sh`. CI fails if it is stale.
* Firmware changes: `esphome config` must pass. Bump `fw_version` and
  `fw_version_code` and add a CHANGELOG entry.
* Home Assistant changes: `tests/check_config.sh` and `pytest` in
  `integrations/home-assistant` must pass. Add a test for every new gate or
  behaviour.

## Tools and versions

| Tool | Version | Used for |
|---|---|---|
| KiCad | 9.0.9 (Docker `kicad/kicad:9.0.9`, `-full` for 3D renders) | hardware |
| ESPHome | 2026.9.1 | firmware |
| Home Assistant | 2026.2.3 + pytest-homeassistant-custom-component 0.13.316 | blueprint tests |
| Python | 3.13 | scripts, tests |

## Versioning

* Hardware: bump `HW_VERSION` / `PCB_REV` in `hardware/kicad/accessbridge.kicad_pro`
  (text variables), the silkscreen text and `scripts/lib.sh`.
* PCB revision letter for any Gerber change. HW minor for electrical changes.
* Release tags: `HW-<hw>_FW-<fw>` (see [releases/README.md](releases/README.md)).

## Pull requests

Describe what was tested and at which level. Include the ERC/DRC summary for
hardware changes.
