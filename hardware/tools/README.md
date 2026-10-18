# Bootstrap tools (Rev A, incremental Rev B)

These scripts created the first version of the KiCad files. They are **not**
part of the normal workflow; edit `hardware/kicad/*` in KiCad.

| File | Purpose |
|---|---|
| `design.py` | Single source of the Rev A/B intent: parts (value, footprint, MPN, LCSC, sourcing status), pin-to-net map, schematic and PCB placement, silkscreen texts |
| `gen_schematic.py` | Writes `accessbridge.kicad_sch` (pin stubs with labels or power symbols, embedded library symbols, frames, notes). Refuses to write if two wires touch accidentally. |
| `gen_pcb.py` | pcbnew (KiCad 9 Python) steps: `update` (incremental revision of the existing board: add/move parts, apply net changes, rip up only affected tracks, lock the rest), `lock`, `place` (footprints, nets, outline, keep-out, texts), `dsn`/`ses` (Specctra for Freerouting), `clean` (dangling autorouter stubs), `shift` (moves the board onto the drawing sheet, sets the drill/place origin), `finish` (dimensions, GND pours, antenna no-pour area, zone fill) |
| `sexpr.py` | Minimal S-expression reader/writer |
| `route_pcb.sh` | Runs the whole pipeline in Docker (`kicad/kicad:9.0.9`) with Freerouting 2.1.0 |
| `routing/accessbridge-revA.ses` | The Freerouting result used for Rev A |
| `routing/revB/*.ses` | The two incremental Freerouting passes for Rev B (new connections only) |

Freerouting 2.1.0 is **not deterministic**, and its multi-threaded optimizer
occasionally produced broken connections. `route_pcb.sh` therefore runs it
single-threaded with the optimizer disabled. `SES=tools/routing/accessbridge-revA.ses`
reproduces Rev A exactly. In every case, KiCad's DRC is the authority:
the committed board passes it with 0 violations.

```sh
SES=hardware/tools/routing/accessbridge-revA.ses hardware/tools/route_pcb.sh
```

## Rev B (incremental, how it was done)

1. `design.py`: added J6, R22, R23, F2, D13-D16 and C11; R10/R14/R18 moved to
   `V_LOOP`; board widened to 96 mm; H2/H4 moved to x = 92 mm; version HW-1.1 / Rev B.
2. `gen_schematic.py` rewrote the schematic. The UUIDs are deterministic, so all
   existing symbols kept their identity and positions (checked: only additions).
3. `gen_pcb.py update <netlist> accessbridge.kicad_pcb`: added the new
   footprints, applied net changes, removed only the tracks touching re-netted
   pads or new courtyards, redrew outline and silkscreen, then locked all other
   tracks.
4. Freerouting routed only the missing connections. Locked tracks are exported
   as `type fix` and kept by KiCad's SES import. One connection (IN3_A at R18)
   needed a second pass after ripping up the tracks within 4 mm of R18.
5. `clean`, `finish` (pours, dimensions), then DRC: 0 violations, 0 unconnected.
