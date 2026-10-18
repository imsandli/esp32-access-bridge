#!/usr/bin/env bash
# Gerber (Protel extensions), Excellon drill, Gerber ZIP for JLCPCB,
# schematic PDF, mechanical drawing and 3D renders.
# Usage: scripts/export-gerbers.sh [--no-renders]
source "$(dirname "$0")/lib.sh"
cd "$REPO_ROOT"
P=hardware/kicad/accessbridge.kicad_pcb
S=hardware/kicad/accessbridge.kicad_sch
G=hardware/manufacturing/gerber
D=hardware/manufacturing/drill
rm -rf "$G" "$D" && mkdir -p "$G" "$D"

kicad pcb export gerbers -o "$G/" \
  --layers F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts \
  --subtract-soldermask --exclude-value --use-drill-file-origin "$P"
kicad pcb export drill -o "$D/" --format excellon --drill-origin plot --excellon-units mm \
  --excellon-zeros-format decimal --excellon-oval-format alternate \
  --generate-map --map-format pdf "$P"

ZIP="hardware/manufacturing/accessbridge-c6-${HW_VERSION}-rev${PCB_REV}-gerbers.zip"
rm -f "$ZIP"
kipython scripts/tools/make_zip.py "$ZIP" "$G" "$D"

kicad sch export pdf -o hardware/docs/schematic.pdf "$S"
kicad pcb export pdf -o hardware/enclosure/drawings/accessbridge-c6-dimensions.pdf \
  --layers Edge.Cuts,Dwgs.User,F.Fab,F.SilkS --mode-single --include-border-title "$P"
kicad pcb export pdf -o hardware/docs/assembly-top.pdf \
  --layers Edge.Cuts,F.Fab,F.SilkS,F.Courtyard --mode-single --include-border-title "$P"

if [ "${1:-}" != "--no-renders" ]; then
  # 3D renders need the 3D model libraries (kicad/kicad:9.0.9-full)
  IMG=hardware/docs/images
  mkdir -p "$IMG"
  KICAD_IMAGE="${KICAD_IMAGE_FULL:-kicad/kicad:9.0.9-full}"
  kicad pcb render -o "$IMG/pcb-top.png" --side top --width 1600 --height 1100 --quality high "$P"
  kicad pcb render -o "$IMG/pcb-bottom.png" --side bottom --width 1600 --height 1100 --quality high "$P"
  # PCB + 3D models as STEP for the enclosure fit check (origin = board corner)
  kicad pcb export step --subst-models --drill-origin --no-dnp \
    -o hardware/enclosure/models/pcb/accessbridge-c6.step "$P"
  kicad pcb render -o "$IMG/pcb-iso.png" --side top --rotate "-40,0,-30" --zoom 0.9 --width 1600 --height 1100 --quality high "$P"
fi
echo "OK: fabrication data in hardware/manufacturing/"
