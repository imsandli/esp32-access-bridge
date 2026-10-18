# Pinout: AccessBridge C6 HW-1.0 / Rev A

The firmware takes GPIO numbers **only** from
[`firmware/esphome/packages/board.yaml`](../../firmware/esphome/packages/board.yaml).
This table and that file must stay identical. The D-pin to GPIO mapping is
from the Seeed XIAO ESP32C6 wiki pin table.

## XIAO ESP32C6 (U2)

| XIAO pin | Module pad | GPIO | Net | Direction | Function | Notes |
|---|---|---|---|---|---|---|
| D0 | 1 | GPIO0 | `IN1_SIG` | in | UA-Hub relay contact | Opto U3. LOW = contact closed. 10k pull-up R12, RC 1k/10n |
| D1 | 2 | GPIO1 | `IN2_SIG` | in | Doorbell contact | Opto U4. LOW = closed |
| D2 | 3 | GPIO2 | `IN3_SIG` | in | DPS reed (input mode) | Opto U5. LOW = closed |
| D3 | 4 | GPIO21 | `DPS_DRV` | out | DPS SSR U6 LED | HIGH = SSR closed. 470R series, 10k pull-down R9 |
| D4 | 5 | GPIO22 | `SDA` | i/o | Qwiic J3 | 4.7k pull-up R4 |
| D5 | 6 | GPIO23 | `SCL` | i/o | Qwiic J3 | 4.7k pull-up R5 |
| D6 | 7 | GPIO16 | `LED_STAT_DRV` | out | Status LED D5 (red) | HIGH = on. GPIO16 is UART0 TX: the LED may flicker during ROM boot |
| D7 | 8 | GPIO17 | `BTN_PAIR` | in | PAIR button SW1 | LOW = pressed. 10k pull-up R3 |
| D8 | 9 | GPIO19 | `OUT_DRV` | out | Open-drain output Q1 | HIGH = J4 OUT- switched to GND. 100R gate, 10k pull-down R7 |
| D9 | 10 | GPIO20 | `EXP_GPIO20` | - | J5 pin 2 | Header not populated |
| D10 | 11 | GPIO18 | `EXP_GPIO18` | - | J5 pin 3 | Header not populated |
| 3V3 | 12 | - | `+3V3` | out | 3.3 V from the XIAO regulator | Pull-ups, Qwiic, J5 |
| GND | 13 | - | `GND` | - | Ground | |
| 5V | 14 | - | `+5V_XIAO` | in | 5 V from buck via D3 | Seeed: diode required for external 5 V |
| - | (module internal) | GPIO3 | - | out | RF switch enable | Firmware drives LOW at boot |
| - | (module internal) | GPIO14 | - | out | Antenna select | LOW = ceramic (default), HIGH = U.FL |

None of the GPIOs used are ESP32-C6 strapping pins. On the XIAO, GPIO9 is the
BOOT button and GPIO15 the user LED; neither is used by this board. ESPHome
reports no strapping-pin warning for this configuration.

## Terminals

| Terminal | Pin | Silkscreen | Net | Description |
|---|---|---|---|---|
| J1 | 1 | POWER `+12V` | `+12V_IN` | UA-Hub LINE 12 V (+) |
| J1 | 2 | POWER `GND` | `GND` | UA-Hub LINE 12 V (-) |
| J1 | 3 | RELAY `COM` | `IN1_COM` | UA-Hub relay COM (dry contact) |
| J1 | 4 | RELAY `NO` | `IN1_NO` | UA-Hub relay NO (dry contact) |
| J2 | 1 | BELL `COM` | `IN2_COM` | Doorbell coupling-relay contact |
| J2 | 2 | BELL `NO` | `IN2_NO` | Doorbell coupling-relay contact |
| J2 | 3 | `DPS-A` | `DPS_A` | DPS port contact A |
| J2 | 4 | `DPS-B` | `DPS_B` | DPS port contact B |
| J4 | 1 | `OUT+` | `+12V` | +12 V (protected, behind F1/D2) for the load |
| J4 | 2 | `OUT-` | `OUT_SW` | Low side, switched to GND by Q1 |
| J3 | 1-4 | `QWIIC 3V3` | GND, +3V3, SDA, SCL | JST SH 1.0 mm, SparkFun Qwiic pin order |
| J5 | 1-4 | - | +3V3, GPIO20, GPIO18, GND | 2.54 mm header (not populated) |

The pinout is also printed on the back silkscreen.

## Solder jumpers (DPS port mode)

| JP1 / JP2 | Mode | Firmware package |
|---|---|---|
| 1-2 bridged (**factory default**, copper bridge) | DPS **input**: reed contact read by opto U5 | `door-position.yaml` |
| cut 1-2, solder 2-3 on **both** jumpers | DPS **output**: U6 PhotoMOS contact between DPS-A and DPS-B | remove `door-position.yaml` (output control planned for FW-1.1.0) |

Never bridge 1-2-3 together.
