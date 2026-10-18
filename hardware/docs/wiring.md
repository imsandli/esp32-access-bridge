# Wiring: classic UniFi Access UA-Hub

> **Safety**
> * AccessBridge is a 12 V SELV device. **Never connect mains voltage
>   (230 V / 120 V) to any terminal.**
> * Work on the doorbell's 230 V side (coupling relay) must be done by a
>   qualified electrician, following local regulations (in Switzerland:
>   NIV/NIN).
> * Disconnect the UA-Hub's PoE before wiring.

## Before you start: verify on site

These UA-Hub properties are not (or not unambiguously) documented in the
sources available for this design. Measure and record them:

| Check | How | Expected |
|---|---|---|
| LINE output always on | Multimeter on LINE (+)/(-) while the door is idle, during an unlock, and after a hub reboot | ~12 V DC at all times |
| Relay mode | Check the Lock (or Aux) relay jumper and the UniFi Access settings | **Dry**. In powered mode, 12 V appears on NO/COM. AccessBridge survives this, but the input then won't work as intended. |
| Relay function | UniFi Access: the relay used must be the one activated on an **authorized unlock** | Closes for the configured unlock duration (several seconds) |
| Free relay | Is the relay already driving an electric strike? | If yes, use the Aux relay, or wire the strike and AccessBridge as described below |

## Terminal assignment

```
          J1 (POWER | RELAY)                 J2 (BELL | DPS)           J4 (OUT)
   +-------+-------+-------+-------+  +------+------+------+------+  +------+------+
   | +12V  |  GND  |  COM  |  NO   |  | COM  |  NO  |DPS-A |DPS-B |  | OUT+ | OUT- |
   +-------+-------+-------+-------+  +------+------+------+------+  +------+------+
      |       |       |       |
      |       |       |       +---- UA-Hub relay NO   (dry contact)
      |       |       +------------ UA-Hub relay COM  (dry contact)
      |       +-------------------- UA-Hub LINE 12V (-)
      +---------------------------- UA-Hub LINE 12V (+)
```

The supply (J1 pins 1-2) and the potential-free contact (J1 pins 3-4) are
separate circuits. The contact loop is powered by AccessBridge itself (about
3.3 mA from the board's 12 V rail through 2.2 kΩ + opto LED + 1 kΩ). **Do not**
connect any voltage to COM/NO.

### Recommended cable

* Power and relay: 4-wire twisted pair (for example CAT5e/CAT6, pairs:
  +12V/GND, COM/NO), up to a few metres within the same cabinet.
* Conductor size for the screw terminals: 0.14 to 1.5 mm² (Phoenix MKDS 1,5
  family). Use ferrules for stranded wire.

## UA-Hub relay variants

**A. Lock relay in dry mode (recommended if no electric strike is used):**
UA-Hub Lock `COM` to J1 `COM`, UA-Hub Lock `NO` to J1 `NO`.

**B. Aux relay in dry mode:** the same with the Aux terminals, if UniFi Access
is configured to operate Aux on unlock. This is not verified: check it in your
UniFi Access version.

**C. Relay already drives a strike:** do **not** connect AccessBridge in
parallel to a powered output. Use the second (Aux) relay, or a separate
coupling relay.

## USB-C power input (optional, J6, Rev B)

J6 is a **power-only** USB-C receptacle (5 V, USB-C sink with 5.1 kΩ CC
resistors), so any USB-C charger or a PC port works. The whole board runs from it,
contact inputs included, which is handy on the bench or as a fallback. Notes:

* **No data.** Firmware upload uses the XIAO's own USB-C (15 mm to the left on
  the same edge).
* USB and 12 V may be connected at the same time. Diodes OR the sources and
  block back-feeding.
* On USB alone, the contact-loop current drops to about 1.1 mA (enough for the
  optocouplers, but less wetting current for the relay contacts). **J4 OUT+ has
  no power on USB alone** (12 V only).
* For the permanent installation, prefer the UA-Hub LINE 12 V.

## Doorbell (optional, J2 BELL)

If your bell push switches 230 V directly:

```
 230 V L ---[bell push]---+------------- bell (rings as before)
                          |
                          +--- A1  coupling relay coil 230 V AC (e.g. Finder 38.51 / 34.51 series,
 230 V N -----------------+--- A2  DIN rail, certified, installed by an electrician)
                                 relay contact 11/14 (dry) ---- 2-wire SELV cable ---- J2 BELL COM / NO
```

* Only the **dry contact** of the coupling relay is connected to AccessBridge.
* The coupling relay provides the mains isolation. AccessBridge never sees
  230 V.
* For a bell transformer system (8-24 V AC), a coupling relay with a matching
  low-voltage AC coil can be used in the same way.

## DPS port (optional, J2 DPS-A / DPS-B)

**Input mode (factory default, JP1/JP2 = 1-2):** connect a **separate** reed
contact, or the second contact of a dual reed, between DPS-A and DPS-B.
**Never** connect it in parallel with the reed that already feeds the UA-Hub
DPS input: the AccessBridge loop current would flow into the hub's input.

**Output mode (JP1/JP2 = 2-3; firmware support planned for FW-1.1.0):**
DPS-A/DPS-B become a PhotoMOS contact (CPC1014N, 60 V / 400 mA, normally
open) that you wire to the UA-Hub DPS input instead of a reed. Unpowered, or
with firmware 1.0.0, the contact is **open**, so the UA-Hub sees the door as
open.

## Open-drain output (optional, J4)

A load (buzzer, indicator, small relay coil at 12 V) between `OUT+` (+12 V)
and `OUT-`. Max. **100 mA** (power budget). The flyback diode D12 is on board.
Zigbee control is planned for FW-1.1.0; FW-1.0.0 keeps the output off.

## Commissioning

1. Wire J1 **without** the XIAO plugged in. Apply PoE to the UA-Hub (or, for
   a bench test, plug a USB-C charger into J6).
2. Check the PWR LED (green). Measure about 5 V on the XIAO socket pin 14
   (5V) against pin 13 (GND), and confirm the voltage is behind D3 (about
   4.6-4.8 V).
3. Remove power, plug in the flashed XIAO (USB-C towards the board edge),
   power up again.
4. Pair with Zigbee2MQTT ([installation.md](../../docs/installation.md)).
5. Run the commissioning tests in [testing.md](../../docs/testing.md).
