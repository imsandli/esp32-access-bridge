#!/usr/bin/env bash
# 3D-printed enclosure: export STEP/STL of all parts, run the fit check against
# the PCB STEP (hardware/enclosure/models/pcb/accessbridge-c6.step, produced by
# scripts/export-gerbers.sh) and render the preview images.
# Needs: pip install -r hardware/enclosure/requirements.txt
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python3}"
E=hardware/enclosure
"$PY" "$E/models/accessbridge_enclosure.py" --out "$E/models"
"$PY" "$E/check_fit.py" --render "$E/drawings"
"$PY" "$E/crop_previews.py"
"$PY" scripts/tools/check_enclosure_models.py "$E/models" "$E/models"
