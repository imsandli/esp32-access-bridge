#!/usr/bin/env bash
# Full BOM, JLCPCB assembly BOM and JLCPCB CPL (pick and place).
source "$(dirname "$0")/lib.sh"
cd "$REPO_ROOT"
B=hardware/manufacturing/bom
C=hardware/manufacturing/pick-and-place
mkdir -p "$B" "$C" build

kicad sch export bom -o "$B/accessbridge-bom-full.csv" \
  --fields 'Reference,Value,Footprint,Manufacturer,MPN,LCSC,LCSC_Status,${QUANTITY},${DNP}' \
  --labels 'Designator,Value,Footprint,Manufacturer,MPN,LCSC,LCSC status,Qty,DNP' \
  --group-by 'Value,Footprint,MPN,LCSC,${DNP}' --ref-range-delimiter '' \
  hardware/kicad/accessbridge.kicad_sch
kicad pcb export pos -o build/accessbridge-pos.csv --format csv --units mm \
  --side front --exclude-dnp --use-drill-file-origin hardware/kicad/accessbridge.kicad_pcb
kipython scripts/tools/jlcpcb.py "$B/accessbridge-bom-full.csv" build/accessbridge-pos.csv \
  "$B/accessbridge-jlcpcb-bom.csv" "$C/accessbridge-jlcpcb-cpl.csv" "$B/accessbridge-manual-assembly.csv"
echo "OK: BOM/CPL in $B and $C"
