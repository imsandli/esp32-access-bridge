# Installation

## 1. Flash the firmware

Either use a release binary (`accessbridge-zigbee-FW-x.y.z-factory.bin`) or
build it yourself:

```sh
python3 -m venv .venv && . .venv/bin/activate
pip install esphome==2026.9.1
cd firmware/esphome
esphome run accessbridge.yaml          # builds and flashes over USB-C
```

With a release binary:

```sh
pip install esptool
esptool.py --chip esp32c6 write_flash 0x0 accessbridge-zigbee-FW-1.0.0-factory.bin
```

If the serial port does not appear, hold **BOOT** on the XIAO while plugging in
the USB-C cable.

Check the log (`esphome logs accessbridge.yaml`): you should see
`AccessBridge C6 HW-1.x, antenna: ceramic` and the Zigbee start message.

## 2. Check the UA-Hub

Follow [hardware/docs/wiring.md, "Before you start"](../hardware/docs/wiring.md#before-you-start-verify-on-site).
In particular:

* **LINE output must be permanently on.** If it is switched (only on during
  unlock, for example), do not use it. Instead, supply AccessBridge from
  another 12 V SELV source in the same cabinet, with its GND tied to the
  UA-Hub GND only through the AccessBridge GND terminal. The relay contact
  still has to be dry. This alternative is not tested.
* Relay in **dry** mode.

## 3. Mount and wire

1. Mount the PCB in the enclosure (USB-C edge towards the USB cut-out,
   terminals towards the cable gland).
2. Wire J1 as in [wiring.md](../hardware/docs/wiring.md#terminal-assignment).
   Doorbell and DPS are optional.
3. Commission without the XIAO first: PWR LED on, about 4.7 V at socket
   pin 14.
4. Plug in the XIAO, USB-C towards the board edge.

## 4. Pair with Zigbee2MQTT

See [integrations/zigbee2mqtt](../integrations/zigbee2mqtt/README.md#pairing):
permit join, power on, wait for the interview, rename, permit join off.
Record the actual property and entity names (test T-Z2M-1).

Status LED (red):

| Pattern | Meaning |
|---|---|
| fast blink (2 Hz) | not joined / searching |
| short blip every 5 s | joined |
| off | no power or firmware not running (check the PWR LED) |

To re-pair: hold **PAIR** 5-15 s.

## 5. Home Assistant

Install the blueprint and create the automation:
[integrations/home-assistant](../integrations/home-assistant/README.md#install).

## 6. Test

Run at least T-FW-6, T-RB-1/2, T-RJ-1, T-HA-1, T-ZB-1, T-UA-2/3 and T-NK-2
from [testing.md](testing.md).
