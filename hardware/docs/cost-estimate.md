# Cost estimate (per board)

> **Estimate only.** Prices were **not** retrieved live: JLCPCB/LCSC, Seeed and
> distributors were not reachable from the design environment. The figures are
> typical 2025/2026 list-price ranges in USD, excluding VAT, customs and import
> fees. Get a real JLCPCB quote with the files in `hardware/manufacturing/`.

## Assumptions

* JLCPCB: 2-layer FR-4 1.6 mm, 86 x 56 mm, green, HASL. SMT assembly top side,
  "Economic" PCBA.
* About 10 unique "extended" LCSC parts (AP63205, EL357N, CPC1014N, inductor,
  PTC, SMAJ15A, SMAJ15CA, JST SH, plus others), each with JLCPCB's extended-part
  loading fee per order (about $3 each).
* Through-hole parts (terminals, sockets) and the XIAO are bought separately
  and soldered by hand.
* Shipping to Switzerland about $20-30 per order (standard/economic shipping).

## Fixed costs per order

| Item | Estimate |
|---|---|
| PCB fabrication (5 boards min., up to 10) | $5-10 |
| PCBA setup + stencil | ~$10 |
| Extended-part loading fees (~10 x $3) | ~$30 |
| Shipping | $20-30 |
| **Fixed total** | **~$65-80** |

## Variable costs per board

| Item | Estimate |
|---|---|
| SMT parts (LCSC prices, see BOM) | $2.50-4.00 |
| SMT assembly (joints) | ~$0.50 |
| Seeed XIAO ESP32C6 | $5-7 |
| 2x 4-pin + 1x 2-pin 5.08 mm screw terminal (Phoenix MKDS) | $3-8 (generic clones: ~$1) |
| 2x female header 1x7 | ~$0.50 |
| Hammond 1591XXD + cable gland + 4 nylon standoffs | $12-20 |
| **Variable total** | **~$24-40** |

## Estimated cost per finished unit

| Quantity | Fixed share | Variable | **Per unit** |
|---|---|---|---|
| 2 (JLCPCB minimum PCBA quantity; 5 bare PCBs are made anyway) | $33-40 | $24-40 | **~$55-80** |
| 5 | $13-16 | $24-40 | **~$37-56** |
| 10 | $7-8 | $24-40 | **~$31-48** |

The enclosure and terminals dominate. Generic terminals and a smaller
enclosure reduce the cost by about $10 per unit.
