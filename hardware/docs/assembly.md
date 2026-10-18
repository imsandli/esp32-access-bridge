# Assembly

## Ordering at JLCPCB (PCB + SMT assembly, top side only)

1. Upload `hardware/manufacturing/accessbridge-c6-HW-1.1-revB-gerbers.zip`.
   * 2 layers, FR-4, 1.6 mm, 1 oz copper, HASL (lead-free) or ENIG, any colour.
   * Board size: 96 x 56 mm (detected from the Gerbers).
2. Enable **PCB Assembly**, top side, "Economic" or "Standard".
3. BOM: `hardware/manufacturing/bom/accessbridge-jlcpcb-bom.csv`.
   CPL: `hardware/manufacturing/pick-and-place/accessbridge-jlcpcb-cpl.csv`.
4. In the JLCPCB BOM matching step:
   * Lines marked "C-number from secondary source: verify" in the Note
     column: check that the matched part has the listed value, package and
     voltage.
   * **R8 (470 Ω 0603)** has no confirmed LCSC number. Pick any 470 Ω 1 %
     0603 basic resistor.
   * Check stock. Every LCSC number was taken from search results during
     design (2026-10); availability changes.
5. **Check the rotation preview** for U1 (TSOT-23-6), U3-U6 (SO-4/SOP-4),
   Q1 (SOT-23), D1-D3/D9-D16 (SMA polarity), D6-D8 (SOD-123) and J6 (USB-C opening
   must face the board edge). JLCPCB's
   footprint origins/rotations sometimes differ from KiCad's. Correct them in
   the preview if needed. This could not be verified without access to
   JLCPCB's tool.

## Manual assembly (through-hole)

From `hardware/manufacturing/bom/accessbridge-manual-assembly.csv`:

| Ref | Part | Notes |
|---|---|---|
| J1, J2 | Screw terminal 4-pin, 5.08 mm, horizontal entry (Phoenix MKDS 1,5/4-5,08, 1715747, or equivalent) | Wire entry towards the board edge |
| J4 | Screw terminal 2-pin, 5.08 mm (Phoenix MKDS 1,5/2-5,08, 1715721, or equivalent) | |
| U2 | 2x female header 1x7, 2.54 mm, about 8.5 mm high | Solder the headers with the XIAO **plugged in**, to keep them aligned |
| U2 | Seeed Studio XIAO ESP32C6 (SKU 113991254) | Plugged in, USB-C towards the board edge. Solder the XIAO's own pin headers (male) |
| J5 | 1x4 pin header (optional) | Not populated by default |

Alternatively, JLCPCB's THT assembly service can fit the terminals and
sockets. They are not in the JLCPCB BOM because no LCSC part numbers were
confirmed.

## After assembly

* Visual inspection: diode polarity (D1, D2, D3, D12 cathode bands), opto
  pin-1 marks, LED polarity.
* Before plugging in the XIAO, follow the commissioning steps in
  [wiring.md](wiring.md).
* Flash the firmware ([installation.md](../../docs/installation.md)).
