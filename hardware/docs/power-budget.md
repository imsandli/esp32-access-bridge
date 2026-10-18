# Power budget

Source: UA-Hub **LINE** output, 12 V DC, max. **0.33 A** (3.96 W), per the
UniFi tech specs and Quick Start Guide. Whether LINE is always on must be
measured on site (see [wiring.md](wiring.md)).

> The XIAO current figures are **estimates**. Seeed specifies 30 mA in
> modem-sleep at 3.8 V. Zigbee TX bursts are higher. The worst-case value
> below is deliberately conservative. **Not measured yet**: test T-EL-3 in
> [testing.md](../../docs/testing.md).

## Loads

| Load | Rail | Typical | Worst case | Basis |
|---|---|---|---|---|
| XIAO ESP32C6 (Zigbee end device, RX on) | 5 V (XIAO LDO) | 40 mA | 150 mA | Estimate. RX always on (non-sleepy end device), TX peaks |
| PWR LED D4 | 5 V | 3 mA | 3 mA | (5 V - 2 V) / 1 kΩ |
| Status LED D5 | 3.3 V | 0.5 mA avg | 1.5 mA | (3.3 V - 1.8 V) / 1 kΩ, mostly off |
| Pull-ups and SSR LED | 3.3 V | 1 mA | 5 mA | SSR LED (3.3 - 1.2 V) / 470 Ω = 4.5 mA when on |
| Contact loops (3x) | 12 V | 0 mA (open) | 18 mA | (12 - 0.35 - 1.2 V) / 3.2 kΩ = 3.3 mA each when closed; ~6 mA each with JP3-JP5 bridged |
| Open-drain output load | 12 V | 0 | 100 mA | Design limit for J4 |

## Conversion to the 12 V input

The buck converter (AP63205, about 80-88 % efficient at these loads; datasheet
efficiency curve not verified for this layout) feeds the XIAO 5V pin through
D3. The XIAO's own LDO makes 3.3 V from that, so the 3.3 V loads are drawn from
5 V as well.

| | Typical | Worst case |
|---|---|---|
| 5 V side (XIAO + LEDs + 3.3 V loads) | ~45 mA = 0.23 W | ~160 mA = 0.80 W |
| 12 V input for that (eff. 85 %) | ~22 mA | ~80 mA |
| + contact loops | 0 | 18 mA |
| + OUT load | 0 | 100 mA |
| **Total at 12 V** | **~25 mA (0.3 W)** | **~200 mA (2.4 W)** |
| UA-Hub LINE limit | 330 mA (3.96 W) | 330 mA (3.96 W) |
| Margin | > 90 % | ~40 % |

F1 (PTC, 200 mA hold / 400 mA trip at 25 °C) limits the total. In a warm
enclosure the hold current drops (typical PTC derating). Keep the OUT load at
or below 100 mA, or replace F1 with a larger hold current, which is safe up to
the 330 mA LINE limit.

## USB-C supply (J6, Rev B)

| Path | Value |
|---|---|
| VBUS from a USB-C sink with 5.1 kΩ CC resistors | 5 V, at least 500 mA from any compliant source |
| F2 PTC | 500 mA hold |
| D13 SS14 into `+5V_XIAO` | XIAO 5V pin at about 4.6 V |
| D16 SS14 into `V_LOOP` | loop current (5 - 0.35 - 1.2 V) / 3.2 kΩ, about 1.1 mA per closed input |
| Total on USB (worst case, no OUT) | about 170 mA |

With JP3-JP5 bridged, about 2 mA per closed input on USB.

With an EL357N CTR of 100 % or more, the optocouplers still sink more than
1 mA against the 0.33 mA the 10 kΩ pull-ups need. Not measured yet: test T-EL-14.

## Wetting-current jumpers (JP3-JP5)

| Case | Current | Dissipation |
|---|---|---|
| Normal, bridged | (11.4 - 1.2 V) / (2.2k ∥ 1k + 1k) = ~6 mA | R24-R26: 17 mW (1206, 250 mW); field 1 kΩ: 36 mW (0603, 100 mW) |
| Wiring fault: COM shorted to GND, bridged | ~15 mA | R24-R26: 104 mW (42 %); R10/R14/R18: 47 mW (47 %); EL357N LED 15 mA (max. 50 mA) |

## Voltage drops

| Element | Drop | Result |
|---|---|---|
| D2 SS14 (reverse polarity) | ~0.3 V at 100 mA | +12V rail ~11.7 V |
| D15 SS14 (+12V into V_LOOP) | ~0.25 V at 10 mA | V_LOOP ~11.4 V on 12 V supply, loop current ~3.2 mA |
| D3 SS14 (XIAO feed) | ~0.35 V at 150 mA | XIAO 5V pin ~4.65 V, enough for the XIAO 3.3 V LDO |
| Buck input range | AP63205: 3.8-32 V | works down to about 6 V input, so long cables are not critical |

## Inrush

The input capacitance is C1 10 µF + C2 100 nF, and C4/C5 2 x 22 µF behind
the buck (soft-start internal to the AP63205). A UA-Hub LINE output that can
drive motion sensors is not expected to trip on this. **Not verified**: test
T-EL-2.
