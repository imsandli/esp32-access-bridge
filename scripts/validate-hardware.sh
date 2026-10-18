#!/usr/bin/env bash
# ERC + DRC (incl. schematic/PCB parity). Exits non-zero on any violation.
# Reports are written to build/reports/.
source "$(dirname "$0")/lib.sh"
cd "$REPO_ROOT"
mkdir -p build/reports
rel() { realpath --relative-to="$REPO_ROOT" "$1"; }

echo "== ERC (all severities, warnings fail)"
kicad sch erc --severity-all --exit-code-violations \
  -o build/reports/erc.rpt "$(rel "$SCH")" || { cat build/reports/erc.rpt; exit 1; }
tail -n 2 build/reports/erc.rpt

echo "== DRC (all severities, schematic parity, warnings fail)"
kicad pcb drc --severity-all --schematic-parity --exit-code-violations \
  -o build/reports/drc.rpt "$(rel "$PCB")" || { cat build/reports/drc.rpt; exit 1; }
grep -E "Found" build/reports/drc.rpt
echo "OK: ERC and DRC clean"
