# Getting started

What you need:

| Item | Notes |
|---|---|
| AccessBridge C6 PCB, assembled | Order from JLCPCB: [hardware/docs/assembly.md](../hardware/docs/assembly.md) |
| Seeed Studio XIAO ESP32C6 | plus 2x 1x7 female headers |
| Hammond 1591XXD enclosure, M3 nylon standoffs, cable gland | [hardware/enclosure](../hardware/enclosure/README.md) |
| UniFi Access UA-Hub (classic) | Lock or Aux relay in **dry** mode |
| Zigbee coordinator with Zigbee2MQTT >= 2.8.0 | |
| Home Assistant with the Nuki integration | |
| Nuki Smart Lock Pro 4 | already working in Home Assistant |
| USB-C data cable, PC with Python 3.11+ | for flashing |

Steps:

1. **Read [security.md](security.md).** Decide whether the remaining risks
   (wiring, Zigbee, MQTT) are acceptable for your door.
2. Build the firmware and flash the XIAO over USB-C:
   [installation.md](installation.md#1-flash-the-firmware).
3. Check the UA-Hub on site (LINE always on, relay mode):
   [hardware/docs/wiring.md](../hardware/docs/wiring.md#before-you-start-verify-on-site).
4. Wire, commission and pair: [installation.md](installation.md).
5. Install the Home Assistant blueprint and configure it:
   [integrations/home-assistant](../integrations/home-assistant/README.md).
6. Run the commissioning and failure tests from [testing.md](testing.md)
   **before relying on the system**.
