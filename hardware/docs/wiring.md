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

## Doorbell (optional)

A 230 V bell push only has two wires: live in, and switched live to the bell.
The bell has two wires too: switched live and neutral. So there is usually
**no permanent live and neutral** in the same place, and **no 230 V device may
be connected to AccessBridge**. Any work on the 230 V side must be done by an
electrician, who also confirms which wire is which (older installations often
use other colours).

The doorbell is informational only: no route below can unlock the door. The
Home Assistant blueprint
[`doorbell-notify.yaml`](../../integrations/home-assistant/automations/doorbell-notify.yaml)
accepts all of them: the AccessBridge `doorbell_pulses` counter, a binary
sensor, or an event entity.

### A. Coupling relay at the bell + battery Zigbee contact sensor (recommended)

```
 230 V L ---[bell push]---+------------- bell (rings as before)
                          |
                          +--- A1  coupling relay coil 230 V AC
 230 V N -----------------+--- A2  (small wall box with a DIN rail, next to the bell)
                                 relay contact (dry) ---- battery Zigbee dry-contact sensor (same box)
```

* The relay coil needs exactly the two wires that already go to the bell, so
  nothing else has to be pulled.
* Relay: Finder **39.41.8.230.5060** (MasterINPUT, 230 V AC coil, 6.2 mm,
  gold-plated contact) or an equivalent certified DIN-rail coupling relay.
  Check the coil-to-contact isolation in the datasheet (reinforced preferred).
* Box: any 2-module surface DIN-rail enclosure, for example Kradex Z106
  (90 x 35 x 65 mm) or Industriegehäuse HS02 35-LP.
* Sensor: a battery Zigbee sensor with a wired dry-contact input, for example
  NodOn SDC-4-1-00 (listed in the Zigbee2MQTT device database). Use it in the
  blueprint as the "doorbell binary sensor".
* Not tested yet: whether the sensor reports a short press (0.2 s) reliably.
  Test T-DB-2.

### B. Coupling relay + cable to AccessBridge J2 BELL

The same relay, with its contact wired over a 2-wire SELV cable to J2 BELL
COM/NO. Use it only if a cable route exists that is separated from the 230 V
wiring.

* With a **gold-contact** relay, leave JP4 open (about 3.3 mA loop current).
* With a relay with **plain silver contacts**, bridge **JP4** (about 6 mA, see
  [Wetting current](#wetting-current-jp3-jp5)).
* For a bell transformer system (8-24 V AC), use a coupling relay with a
  matching low-voltage AC coil.

### C. Shelly in the light-switch frame (only after checking on site)

A Shelly needs a permanent live, which a light-switch box usually has. The
Shelly 1L/2L Gen3 run without neutral (they power themselves through the
lamp). According to Shelly's documentation, however, their inputs expect a
push wired between the Shelly's own `Sx` terminal and `S1`/`S2`. They do not
sense a live wire from another circuit, so they **cannot simply listen to
the existing bell push**. Using one would mean rewiring so that the Shelly
switches the bell. The bell would then depend on the Shelly and on the lamp
being present. Not recommended unless an electrician confirms a clean
solution.

### D. Vibration sensor on the bell (no wiring)

A battery Zigbee vibration sensor stuck to the bell housing. No electrician is
needed, but it may miss presses or false-trigger. Use the blueprint's binary
sensor input.

### Not recommended

* **Shelly i4 / 1 Mini at the bell push:** need neutral and permanent live,
  which are not there.
* **Eltako ER61-UC:** no published minimum contact load and no isolation
  rating for SELV. Its contact can start in either state before the first
  synchronisation, and a contact that starts closed would hide the first
  press.

## Wetting current (JP3-JP5)

Each contact input has a solder jumper that adds 1 kΩ (R24-R26, 1206) in
parallel with its 2.2 kΩ loop resistor:

| Jumper | Input | Open (default) | Bridged |
|---|---|---|---|
| JP3 | IN1 relay (J1) | ~3.3 mA | ~6 mA |
| JP4 | IN2 bell (J2.1/2.2) | ~3.3 mA | ~6 mA |
| JP5 | IN3 DPS input (J2.3/2.4) | ~3.3 mA | ~6 mA |

Bridge a jumper when the contact is a relay with plain silver contacts (for
example the UA-Hub relay, if it turns out to be unreliable, or a non-gold
coupling relay). Leave it open for gold contacts and reed switches. On USB
power only, the current is about 2 mA bridged instead of 1.1 mA.

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
