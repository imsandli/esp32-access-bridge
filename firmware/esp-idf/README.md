# ESP-IDF / Espressif Zigbee SDK fallback: NOT IMPLEMENTED

The project requirements ask for an ESP-IDF implementation **only if ESPHome
cannot meet the requirements reliably**. For FW-1.0.0, ESPHome 2026.9.1
covers every required function:

| Requirement | ESPHome 2026.9.1 |
|---|---|
| Zigbee end device on ESP32-C6 | yes (`zigbee:`, default role end device) |
| Contact as binary sensor | yes (Binary Input cluster, `report: force`) |
| Distinguish state from new event | yes (pulse counter as Analog Input) |
| Configurable debounce | yes (`delayed_on` / `delayed_off`) |
| No false events after restart/rejoin | yes (`trigger_on_initial_state: false`, edge + `is_joined()` checks) |
| Zigbee2MQTT compatible without a converter | yes (generated definitions for Binary/Analog Input, Z2M >= 2.8.0) |

So this directory contains no code. It remains the documented fallback if one
of these becomes true during hardware testing:

* The ESP32-C6 Zigbee link is unreliable with ESPHome. ESPHome's own docs say
  the H2 works more reliably than the C6, and some C6 boards only work next to
  the coordinator. Test T-ZB-4 checks the range.
* Zigbee control of the outputs is needed before ESPHome releases ESP32
  Zigbee switches.

## Outline of the fallback (for a future implementation)

* ESP-IDF v5.x with `espressif/esp-zigbee-lib` (the same component ESPHome
  pins: 2.0.4).
* The same GPIO map as [`../esphome/packages/board.yaml`](../esphome/packages/board.yaml),
  and the same endpoint/cluster layout as ESPHome (Binary Input + Analog
  Input on endpoints 1-3, version on 4), so Zigbee2MQTT and the Home
  Assistant blueprints work unchanged.
* On/Off (or Binary Output) clusters on new endpoints for the DPS SSR and the
  open-drain output, with a link-loss timeout that switches both off.
* The same counting rules as `contact-sensor.yaml`.
