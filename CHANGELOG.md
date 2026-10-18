# Changelog

Hardware and firmware are versioned separately (`HW-x.y` + `Rev X`, `FW-x.y.z`).
The format follows [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Hardware HW-1.1 / Rev B: USB-C power input (not manufactured)

- J6 power-only USB-C (5 V sink, 5.1 kΩ CC, 500 mA PTC, SMAJ5.0A TVS). The whole
  board, contact inputs included, runs from a USB charger; firmware still goes
  through the XIAO's own USB-C.
- New rail `V_LOOP` (diode-OR of +12 V and USB 5 V) for the contact loops;
  USB 5 V diode-ORed into the XIAO 5V pin.
- Board widened to 96 x 56 mm; mounting holes H2/H4 moved to x = 92 mm. All
  Rev A parts kept their positions; Rev A routing kept except around R10/R14/R18.
- Selectable contact wetting current: solder jumpers JP3-JP5 (open by default)
  add R24-R26 (1 kΩ, 1206) in parallel with the loop resistors, ~3.3 mA to ~6 mA,
  for relays with plain silver contacts.
- BOM: R8 = C23179; D4 = KT-0603YG yellow-green (C2289, no green 0603 in stock); optocouplers U3-U5 = UMW EL357C (C725794, same SOP-4 package and CTR rank as EL357N(C)) because of JLCPCB stock.
- ERC/DRC clean (incl. parity).

### Enclosure (new)

- Parametric 3D-printable case (CadQuery): DIN-rail base and wall-screw base,
  shared lid, PAIR plunger and cable clamp. M3 heat-set inserts, M16 gland,
  two USB-C openings.
- Automated fit check against the KiCad STEP of the PCB (CI).


### Hardware HW-1.0 / Rev A: initial design (superseded by Rev B before manufacturing)

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

- Doorbell blueprint accepts the AccessBridge counter, an event entity (e.g. a
  Shelly input) or a binary sensor (e.g. a battery Zigbee contact sensor on a
  coupling relay); 3 new behaviour tests.
- Doorbell wiring options for 230 V installations without neutral at the bell
  push documented (coupling relay at the bell).
- Home Assistant blueprints: Nuki unlatch with counter/freshness/cooldown/enable/door
  gates and failure logging; doorbell notification.
- Behaviour tests on a real HA core; CI workflows for hardware, firmware,
  integrations and releases.
