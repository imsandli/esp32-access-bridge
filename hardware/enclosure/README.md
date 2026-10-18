# Enclosure

## Recommendation: Hammond 1591XXD (ABS, screwed lid)

| | Value | Source |
|---|---|---|
| Model | **Hammond 1591XXDBK** (black) or **1591XXDGY** (grey); **1591XXDFLBK** with mounting flanges | Hammond 1591XX series |
| Outside | 152 x 82 x 51 mm (series table; one listing gives 152 x 81 x 46 mm) | Hammond series page, distributors |
| Max. PCB size | **145 x 75 mm** | Hammond part page 1591XXDBK |
| Lid | Screwed (cover screws included), ABS UL94-HB | Hammond 1591XX series |
| Internal PCB bosses | Box and lid, for #4 x 1/4" self-tapping screws (not included) | Hammond 1591XX series |

Hammond drawings and websites were not reachable from the design
environment; values are from search results of Hammond's pages. **Before
ordering, check the inside height and the boss positions in Hammond's drawing
for 1591XXD.**

### Fit check

| | AccessBridge C6 | 1591XXD | Margin |
|---|---|---|---|
| Length | 86 mm | max. PCB 145 mm | 59 mm |
| Width | 56 mm | max. PCB 75 mm | 19 mm, in front of the screw terminals for wiring |
| Height needed | ~22 mm: standoffs 6 mm + PCB 1.6 mm + sockets 8.5 mm + XIAO incl. USB-C ~5 mm; terminals ~10 mm above PCB | 51 mm outside (inside height to be checked, expected > 40 mm) | > 15 mm (expected) |

The smaller **1591XXC** (max. PCB 114.5 x 60.5 mm, inside 115.15 x 60.65 x 36 mm
per the Hammond drawing) also fits the PCB outline. It was rejected because
only about 2 mm would remain in front of the terminal wire entries.

### Mounting

* AccessBridge has 4 x M3 holes (3.2 mm) at 4 mm from each edge (78 x 48 mm
  pattern; see the [dimension drawing](drawings/accessbridge-c6-dimensions.pdf)).
* Hammond's internal bosses are positioned for Hammond's own reference
  boards. If they do not match the 78 x 48 mm pattern (likely), fix the PCB
  with **M3 x 6 mm nylon standoffs** screwed through 3.2 mm holes drilled in
  the base, or bonded to it. A future PCB revision could adopt the 1591XXD
  boss pattern (open point).
* Place the board with its **USB-C edge about 1-2 mm from a short wall**, so
  the USB-C connector can be reached through a cut-out.

### Machining

| Opening | Wall | Size | Position |
|---|---|---|---|
| USB-C access | wall facing the board's top edge | 12 x 7 mm, rounded | centred on the XIAO (board X = 68 mm from the left edge, see drawing), ~5 mm above PCB top surface + socket height; **measure on the assembled board** |
| Cable entry | wall facing the terminal side | M16 or PG9 cable gland with strain relief, IP54 | centred, at terminal height |

The USB-C cut-out may be left closed and the lid opened for firmware updates
(the XIAO stays reachable). With the cut-out, IP rating drops; use a rubber
plug.

### Files

* [drawings/accessbridge-c6-dimensions.pdf](drawings/accessbridge-c6-dimensions.pdf):
  board outline, holes, USB-C and terminal positions (generated from the PCB).
* `models/`: no enclosure 3D model is included (Hammond's STEP files could not
  be downloaded in the design environment and are not redistributable).
  Download the 1591XXD STEP from Hammond for mechanical CAD.
