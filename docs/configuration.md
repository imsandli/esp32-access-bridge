# Configuration

## Firmware substitutions (`firmware/esphome/accessbridge.yaml`)

| Substitution | Default | Meaning |
|---|---|---|
| `debounce` | `40ms` | `delayed_on` and `delayed_off` for all contact inputs. 30-50 ms suits relay contacts. Pulses shorter than this are ignored. |
| `min_pulse_interval_ms` | `1500` | Minimum time between two counted pulses on the same input (chatter protection) |
| `fw_version` / `fw_version_code` | `1.0.0` / `10000` | Firmware version (change both) |

`firmware/esphome/packages/board.yaml`:

| Substitution | Default | Meaning |
|---|---|---|
| `pin_*` | see [pinout](../hardware/docs/pinout.md) | GPIO assignment for HW-1.0 Rev A. Change only for a different hardware revision. |
| `use_external_antenna` | `"false"` | `"true"` selects the XIAO's U.FL antenna connector (GPIO14 high) |

## Firmware packages

Remove a package line in `accessbridge.yaml` to drop the feature:

| Package | Drop it when |
|---|---|
| `doorbell` | no doorbell connected (the entity would just stay off) |
| `door_position` | DPS port jumpered to **output** mode, or no reed connected |
| `outputs` | never: it keeps the SSR and OUT in their safe (off) state |

After adding or removing entities, re-pair the device (see
[zigbee2mqtt](../integrations/zigbee2mqtt/README.md#after-a-firmware-change)).

## Hardware options

| Option | How |
|---|---|
| DPS port input/output | JP1 + JP2: 1-2 = input (default), 2-3 = SSR output |
| OUT current > 100 mA | Not recommended (power budget). Replace F1 with a 300 mA hold PTC and stay below the 330 mA LINE limit in total. |
| Qwiic | 3.3 V I2C on GPIO22/23, 4.7 kΩ pull-ups fitted. No firmware support in FW-1.0.0. |

## Home Assistant blueprint inputs

See [integrations/home-assistant](../integrations/home-assistant/README.md#install).
Recommended: cooldown 10 s, freshness 15 s, enable switch configured.
