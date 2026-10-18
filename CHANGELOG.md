# Changelog

Hardware and firmware are versioned separately (`HW-x.y` + `Rev X`, `FW-x.y.z`).
The format follows [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Hardware HW-1.0 / Rev A: initial design (not manufactured)

- XIAO ESP32C6 carrier, 86 x 56 mm, 2 layers, KiCad 9.0.9.
- 12 V input from the UA-Hub LINE output: PTC, TVS, reverse-polarity diode,
  AP63205 5 V buck, XIAO 5V feed through a Schottky diode (Seeed guidance).
- Three optocoupler dry-contact inputs (UA-Hub relay, doorbell, DPS) with a
  board-powered loop current.
- DPS port selectable as input or as PhotoMOS contact output (JP1/JP2).
- 12 V open-drain output, Qwiic port, PAIR button, power and status LEDs.
- ERC/DRC clean. JLCPCB fabrication data reproducible from the sources.

### Firmware FW-1.0.0 (not tested on hardware)

- ESPHome 2026.9.1 Zigbee end device.
- `relay_contact`, `relay_pulses`, `doorbell`, `doorbell_pulses`,
  `door_closed`, `fw_version`.
- Pulses only counted on a debounced open-to-closed edge from a known state,
  while joined, with a minimum interval.
- PAIR long-press for leave/factory reset. Status LED shows the join state.
- Outputs held off (Zigbee control planned for FW-1.1.0).

### Integrations

- Home Assistant blueprints: Nuki unlatch with counter/freshness/cooldown/enable/door
  gates and failure logging; doorbell notification.
- Behaviour tests on a real HA core; CI workflows for hardware, firmware,
  integrations and releases.
