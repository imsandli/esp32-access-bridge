# Test plan

Test levels, and what each one proves:

| Level | Meaning |
|---|---|
| **Statically checked** | Schema, rule or design checks (ERC, DRC, `esphome config`, HA `check_config`) |
| **Compiled** | Firmware builds for the target |
| **Software-tested** | Behaviour tests in a real software runtime (HA core) |
| **Electrically tested** | Measured on an assembled PCB |
| **Z2M tested** | Paired and observed in Zigbee2MQTT |
| **UA-Hub tested** | Driven by a real classic UA-Hub |
| **Nuki tested** | End to end with a real Nuki Smart Lock Pro 4 |

AccessBridge must not be called *hardware-tested* until the electrical tests
below have been run on a physical board and recorded here.

## Current status (HW-1.1 Rev B + FW-1.0.0)

| Level | Status | Evidence |
|---|---|---|
| Statically checked | **done** | ERC 0/0, DRC 0 violations / 0 unconnected / 0 parity (CI `hardware`); `esphome config` OK; HA `check_config` OK |
| Compiled | **done** | CI `firmware` (ESPHome 2026.9.1) |
| Software-tested | **done** | 12/12 blueprint tests (CI `integrations`, HA 2026.2.3) |
| Enclosure fit-checked | **done** | `hardware/enclosure/check_fit.py` (CI `hardware` / enclosure job): no collision, lid clearance, USB-C cut-outs, gland, inserts vs antenna |
| Electrically tested | not started | no PCB manufactured yet |
| Z2M tested | not started | |
| UA-Hub tested | not started | |
| Nuki tested | not started | |

Record results as `PASS` / `FAIL` with the date, HW revision, FW version and
tester in the result column, and commit the change.

## 1. Electrical (bench, lab supply 12 V / current limit 0.4 A)

| ID | Test | Expected | Result |
|---|---|---|---|
| T-EL-1 | Visual: polarity of D1-D3, D12, LEDs, U1, U3-U6 | as on the assembly drawing | |
| T-EL-2 | Power up without XIAO, measure input current and +5V | < 10 mA; 5.0 V ± 3 %; PWR LED on; no oscillation (scope SW node) | |
| T-EL-3 | XIAO plugged in, joined: average and peak input current | average < 50 mA, peak < 150 mA (budget: power-budget.md) | |
| T-EL-4 | Reverse-polarity supply (current limit 0.4 A) | no damage; F1 trips or limits; recovers when corrected | |
| T-EL-5 | Input voltage sweep 9-15 V | +5V stays in regulation | |
| T-EL-6 | XIAO 5V pin with USB-C connected **and** 12 V supply | no back-feed into the buck (D3 blocks), USB host OK | |
| T-EL-7 | Contact loop current (COM-NO shorted) per input | 3.0-3.6 mA | |
| T-EL-8 | INx_SIG level open/closed | open > 3.0 V, closed < 0.4 V | |
| T-EL-9 | 12 V applied across COM/NO (miswiring, both polarities) | no damage; input reads closed or open, never anything else | |
| T-EL-10 | ESD (if equipment available): ±4 kV contact on J1/J2 terminals | no reset, no damage | |
| T-EL-11 | DPS output mode (JP 2-3): SSR contact resistance when driven (GPIO21 high via test firmware) | < 2 Ω; open when unpowered | |
| T-EL-12 | OUT: 100 mA load, Q1 temperature | < 50 °C rise | |
| T-EL-13 | Thermal: 1 h in closed enclosure, 25 °C ambient | no part > 60 °C | |
| T-EL-14 | USB-C (J6) only, 5 V charger, no 12 V | XIAO runs; contact inputs work (loop current ~1.1 mA, INx_SIG < 0.4 V closed); OUT dead (expected) | |
| T-EL-15 | J6 USB-C and 12 V at the same time | no back-feed (VBUS < 5.3 V, +12V unchanged); D13/D3 OR works | |
| T-EL-16 | J6 USB-C and XIAO USB-C (PC) at the same time | PC enumerates the XIAO; flashing works; no back-feed into the PC beyond Seeed's diode rule | |
| T-EL-17 | Non-PD USB-C charger and a USB-A to USB-C cable | board powers up (5.1 kΩ CC sink resistors) | |

## 2. Firmware on hardware

| ID | Test | Expected | Result |
|---|---|---|---|
| T-FW-1 | Flash FW-1.0.0 over USB-C, boot log | `AccessBridge C6 HW-1.x, antenna: ceramic`, Zigbee started | |
| T-FW-2 | Contact pulse 200 ms (signal generator + relay) | 1 x `relay pulse #n`; counter +1 | |
| T-FW-3 | Contact pulse 20 ms (< debounce 40 ms) | not counted | |
| T-FW-4 | Bouncing contact (10 bounces within 5 ms, then held) | exactly 1 pulse | |
| T-FW-5 | Two pulses 500 ms apart | 2nd: "within 1500 ms of previous pulse", not counted | |
| T-FW-6 | Contact **closed** during power-up | no pulse counted; state = closed | |
| T-FW-7 | Contact pulse while not joined (coordinator off) | "Zigbee not joined", not counted; nothing sent after the rejoin | |
| T-FW-8 | Status LED | fast blink unjoined, blip every 5 s joined | |
| T-FW-9 | PAIR held 2 s / 7 s / 20 s | nothing / leave + reset + rejoin / nothing | |
| T-FW-10 | Outputs after boot | DPS SSR off, OUT off | |

## 3. Zigbee2MQTT

| ID | Test | Expected | Result |
|---|---|---|---|
| T-Z2M-1 | Pair with Z2M >= 2.8.0 | generated definition; exposes per integrations/zigbee2mqtt/README.md; **record the actual property names** | |
| T-Z2M-2 | Pulse | `relay_contact` ON then OFF; `relay_pulses` +1 within 1 s | |
| T-Z2M-3 | Device reboot (power cycle) | counter 0; contact state reported; no other change | |
| T-Z2M-4 | Range: device in final position, link quality | LQI recorded; stable for 24 h (ESPHome notes C6 range issues; try `use_external_antenna` with a U.FL antenna if poor) | |
| T-Z2M-5 | Coordinator restart | device rejoins; no counter change | |

## 4. Restart and failure scenarios (system, with HA blueprint)

| ID | Scenario | Expected | Result |
|---|---|---|---|
| T-RB-1 | AccessBridge power cycle with relay open | no unlatch | |
| T-RB-2 | AccessBridge power cycle with relay **closed** | no unlatch | |
| T-RJ-1 | Zigbee rejoin (coordinator restart, device moved) | no unlatch | |
| T-HA-1 | Home Assistant restart | no unlatch; logbook shows nothing for restored states | |
| T-HA-2 | Zigbee2MQTT restart | no unlatch | |
| T-ZB-1 | Coordinator off, UA-Hub access, coordinator on after 2 min | no unlatch now or later; device log shows "not joined" | |
| T-ZB-2 | Pulse with HA stopped, HA started 2 min later | no unlatch (freshness) | |
| T-PW-1 | UA-Hub PoE off/on | AccessBridge reboots; no unlatch | |
| T-PW-2 | Brown-out: supply ramp 12 V to 4 V to 12 V | clean reboot; no unlatch | |
| T-CD-1 | Two accesses 3 s apart | one unlatch; the second is logged as cooldown | |
| T-NK-1 | Nuki offline (batteries out), access granted | error in the system log "FAILED or was not confirmed" | |

## 5. UA-Hub and Nuki (end to end)

| ID | Test | Expected | Result |
|---|---|---|---|
| T-UA-1 | Measure LINE output at idle/unlock/hub reboot | constant ~12 V (else installation.md alternative) | |
| T-UA-2 | Valid credential at reader | relay closes for the unlock time; Nuki unlatches within 3 s | |
| T-UA-3 | Invalid credential | relay stays open; nothing happens | |
| T-UA-4 | Remote unlock from the UniFi Access app | same as T-UA-2 (if the relay is driven) | |
| T-NK-2 | Physical key from outside with the Nuki mounted | door opens | |
| T-NK-3 | Enable switch off | access logged as "disabled", no unlatch | |
| T-NK-4 | Door open (DPS input), access granted | no unlatch, "door already open" | |

## 6. Mechanical

| ID | Test | Expected | Result |
|---|---|---|---|
| T-ME-1 | Printed base (PETG/ASA): PCB on heat-set inserts | fits; lid closes; terminals reachable | |
| T-ME-4 | DIN variant on a TS35 rail | snaps on, holds, releases with a screwdriver | |
| T-ME-5 | Wall variant | mounts with 2 screws through the flange slots | |
| T-ME-6 | PAIR plunger + LED light holes | button operable through the lid; LEDs visible | |
| T-ME-7 | M16 gland + clamp bar | gland nut fits; cables clamped | |
| T-ME-8 | Zigbee range in the closed case vs. open (LQI) | no significant loss | |
| T-ME-2 | USB-C (XIAO and J6) through the cut-outs with standard cables | both plug fully (wall 1.2 mm at the recesses); XIAO cut-out height matches the real socket stack | |
| T-ME-3 | Cable gland + strain relief | 50 N pull without moving the terminals | |

## Firmware/hardware compatibility record

| Firmware | Hardware | Tested levels | Date |
|---|---|---|---|
| FW-1.0.0 | HW-1.1 Rev B | statically checked, compiled, software-tested, enclosure fit-checked (CadQuery vs PCB STEP) | 2026-10-18 |
