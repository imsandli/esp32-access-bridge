# AccessBridge Zigbee firmware

**FW-1.0.0**, ESPHome **2026.9.1**, ESP-IDF framework, target AccessBridge C6
HW-1.1 Rev B (Seeed XIAO ESP32C6); the GPIO map is identical on HW-1.0 Rev A. MIT licence.

| Status | |
|---|---|
| `esphome config` | passes (local and CI) |
| `esphome compile` | passes in CI ([firmware workflow](../.github/workflows/firmware.yml)) |
| Runs on hardware | **not tested** |
| Pairs with Zigbee2MQTT | **not tested** |

## What it does

Zigbee **end device** (not a router or coordinator). No Wi-Fi, no ESPHome API,
no OTA, no cloud.

| Zigbee entity | Endpoint | Cluster | Meaning |
|---|---|---|---|
| `relay_contact` | 1 | Binary Input | UA-Hub relay contact, on = closed |
| `relay_pulses` | 1 | Analog Input | New, counted closures since boot |
| `doorbell` | 2 | Binary Input | Doorbell coupling-relay contact |
| `doorbell_pulses` | 2 | Analog Input | New doorbell presses since boot |
| `door_closed` | 3 | Binary Input | DPS reed (input mode only), on = closed |
| `fw_version` | 4 | Analog Input | 10000 = 1.0.0 (MAJOR*10000 + MINOR*100 + PATCH) |

The Basic cluster reports manufacturer `esphome`, model `accessbridge` and the
build date code.

Counting rules and link-loss behaviour: [docs/security.md](../docs/security.md).
Configuration options: [docs/configuration.md](../docs/configuration.md).

## Layout

```
esphome/
  accessbridge.yaml            entry point: versions, substitutions, package list
  secrets.example.yaml         template only (no secrets are needed)
  packages/
    board.yaml                 the only place with GPIO numbers + RF switch init
    zigbee.yaml                Zigbee role, join logging, PAIR button, status LED, fw_version
    contact-sensor.yaml        UA-Hub relay input + pulse counter
    doorbell.yaml              doorbell input + pulse counter
    door-position.yaml         DPS reed input (remove for DPS output mode)
    outputs.yaml               DPS SSR and open-drain output held OFF (no Zigbee control yet)
esp-idf/README.md              fallback plan (not implemented)
tests/README.md                what is tested where
```

The packages separate the Zigbee behaviour (`zigbee.yaml`) from GPIO
detection (`contact-sensor.yaml`, `doorbell.yaml`, `door-position.yaml`).

## Build

```sh
python3 -m venv .venv && . .venv/bin/activate
pip install esphome==2026.9.1
cd firmware/esphome
esphome config accessbridge.yaml
esphome compile accessbridge.yaml
```

The first compile downloads the ESP-IDF toolchain and `espressif/esp-zigbee-lib`
2.0.4 (pinned by ESPHome).

## Flash (USB-C)

Zigbee has no OTA in ESPHome, so updates go over USB:

```sh
esphome run accessbridge.yaml --device /dev/ttyACM0
# or with a CI/release binary:
esptool.py --chip esp32c6 write_flash 0x0 accessbridge-zigbee-FW-1.0.0-factory.bin
```

If the port does not appear, hold the XIAO **BOOT** button while plugging in
USB-C.

**After changing entities or names**, ESPHome requires removing the device
from Zigbee2MQTT and re-pairing it, with a re-interview. See
[docs/installation.md](../docs/installation.md).

## Versioning

* Firmware versions are `FW-MAJOR.MINOR.PATCH`, set in `accessbridge.yaml`
  (`fw_version`, `fw_version_code`). Bump both and add a CHANGELOG entry.
* Each release states the hardware revision it was tested with. See
  [releases/README.md](../releases/README.md).

## Planned (not implemented)

| Feature | Blocker | Target |
|---|---|---|
| Zigbee control of the DPS SSR and the open-drain output | ESPHome 2026.9.x has Zigbee switches only on nRF52. ESP32 support exists on the ESPHome `dev` branch (not released) | FW-1.1.0 |
| Zigbee OTA | Not supported by ESPHome Zigbee | - |
| I2C sensors on Qwiic | No use case defined | - |
