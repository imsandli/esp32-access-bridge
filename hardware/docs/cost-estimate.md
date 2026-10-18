# Cost estimate (per board)

> **Estimate only.** Prices were **not** retrieved live: JLCPCB/LCSC, Seeed and
> distributors were not reachable from the design environment. The figures are
> typical 2025/2026 list-price ranges in USD, excluding VAT, customs and import
> fees. Get a real JLCPCB quote with the files in `hardware/manufacturing/`.

## Assumptions

* JLCPCB: 2-layer FR-4 1.6 mm, 96 x 56 mm, green, HASL. SMT assembly top side,
  "Economic" PCBA.
* About 13 unique "extended" LCSC parts (AP63205, EL357C, CPC1014N, inductor,
  PTCs, SMAJ15A, SMAJ15CA, SMAJ5.0A, JST SH, USB-C, plus others), each with JLCPCB's extended-part
  loading fee per order (about $3 each).
* Through-hole parts (terminals, sockets) and the XIAO are bought separately
  and soldered by hand.
* Shipping to Switzerland about $20-30 per order (standard/economic shipping).

## Fixed costs per order

| Item | Estimate |
|---|---|
| PCB fabrication (5 boards min., up to 10) | $5-10 |
| PCBA setup + stencil | ~$10 |
| Extended-part loading fees (~13 x $3) | ~$40 |
| Shipping | $20-30 |
| **Fixed total** | **~$75-90** |

## Variable costs per board

| Item | Estimate |
|---|---|
| SMT parts (LCSC prices, see BOM) | $2.50-4.00 |
| SMT assembly (joints) | ~$0.50 |
| Seeed XIAO ESP32C6 | $5-7 |
| 2x 4-pin + 1x 2-pin 5.08 mm screw terminal (Phoenix MKDS) | $3-8 (generic clones: ~$1) |
| 2x female header 1x7 | ~$0.50 |
| USB-C power input (J6 + 8 small parts, Rev B) | ~$0.70 |
| 3D-printed case: ~85 g PETG/ASA + 8 M3 heat-set inserts + 8 M3 screws + M16 gland (or: Hammond 1591XXD, $12-20) | $4-7 |
| **Variable total** | **~$17-28** (printed case) |

## Estimated cost per finished unit

| Quantity | Fixed share | Variable | **Per unit** |
|---|---|---|---|
| 2 (JLCPCB minimum PCBA quantity; 5 bare PCBs are made anyway) | $38-45 | $17-28 | **~$55-73** |
| 5 | $15-18 | $17-28 | **~$32-46** |
| 10 | $8-9 | $17-28 | **~$25-37** |

The XIAO and the terminals dominate. With the Hammond enclosure instead of the
printed case add about $10-15 per unit. Generic terminals save about $4.
