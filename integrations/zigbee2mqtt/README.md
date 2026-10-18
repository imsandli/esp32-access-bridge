# Zigbee2MQTT

**No external converter is needed** (and none is shipped). The AccessBridge
firmware only uses standard ZCL clusters. Zigbee2MQTT builds a *generated
definition* for unknown devices, with an expose for each `genBinaryInput` and
`genAnalogInput` endpoint (`zigbee-herdsman-converters`,
`src/lib/generateDefinition.ts`). The `description` attribute, which is the
ESPHome entity name, becomes the label.

Requirements: **Zigbee2MQTT >= 2.8.0** (the ESPHome Zigbee docs require it for
ESPHome devices with several endpoints).

> **Not yet tested with a real device.** The exact property names below are
> derived from the converter source and must be confirmed during the first
> pairing (test T-Z2M-1 in [docs/testing.md](../../docs/testing.md)).

## Expected exposes

| ESPHome entity | Endpoint | Expected Z2M property | Type | HA entity (via MQTT discovery) |
|---|---|---|---|---|
| `relay_contact` | 1 | `binary_input_1` | binary (ON/OFF) | binary sensor "relay_contact" |
| `relay_pulses` | 1 | analog input of endpoint 1 | numeric | sensor "relay_pulses" |
| `doorbell` | 2 | `binary_input_2` | binary | binary sensor "doorbell" |
| `doorbell_pulses` | 2 | analog input of endpoint 2 | numeric | sensor "doorbell_pulses" |
| `door_closed` | 3 | `binary_input_3` | binary | binary sensor "door_closed" |
| `fw_version` | 4 | analog input of endpoint 4 | numeric | sensor "fw_version" |

Manufacturer: `esphome`, model: `accessbridge`.

## Pairing

1. Zigbee2MQTT frontend: **Permit join (All)**.
2. Power the AccessBridge. A factory-new device joins on its own. The red
   status LED blinks fast while it is not joined, and blips every 5 s once
   joined.
3. Wait for the interview to finish. The device shows as "Generated" /
   unsupported-but-working with the exposes above.
4. Rename the device, for example `accessbridge`.
5. **Permit join off.**

### Re-pairing / moving to another network

Hold **PAIR** (SW1) for 5-15 s. The device leaves the network, clears its
Zigbee data, reboots and joins again (permit join must be on). In
Zigbee2MQTT, remove the old device first.

### After a firmware change

ESPHome: "Whenever the configuration is changed, the device should be removed
and re-added to the Zigbee network ... the device must also be re-interviewed."
So: remove it in Z2M, hold PAIR for 5-15 s, and pair again.

## Recommended settings

* Leave the device's reporting configuration as generated. The firmware also
  sends forced reports on every change (`report: force`).
* Availability: enable Zigbee2MQTT availability (active, 10 min or less) so
  Home Assistant shows `unavailable` when the link is lost. The blueprints
  ignore all transitions from `unavailable`.
