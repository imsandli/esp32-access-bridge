#!/usr/bin/env bash
# Bootstrap pipeline used to create hardware/kicad/accessbridge.kicad_{sch,pcb}.
# NOT part of the normal workflow: after bootstrap the KiCad files are edited
# directly in KiCad. Kept for transparency and reproducibility of Rev A.
#
# Requirements: docker (kicad/kicad:9.0.9 and :9.0.9-full), Java 21,
# Freerouting 2.1.0 jar (FREEROUTING_JAR), Python 3.
#
# Steps: schematic generation -> ERC -> netlist -> placement -> Specctra DSN
#        -> Freerouting -> SES import -> stub cleanup -> GND pours -> DRC
set -euo pipefail
HW="$(cd "$(dirname "$0")/.." && pwd)"
B="$HW/../build/bootstrap"
mkdir -p "$B"
IMG="${KICAD_IMAGE:-kicad/kicad:9.0.9}"
JAR="${FREEROUTING_JAR:-/opt/freerouting/freerouting-2.1.0.jar}"
SYMDIR="$B/symbols"

run() {  # run a shell snippet inside the KiCad container, cwd = hardware/kicad
  docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp/home -v "$HW:/w" -v "$B:/b" -w /w/kicad "$IMG" sh -c \
    'mkdir -p $HOME/.config/kicad/9.0 && cp /usr/share/kicad/template/*-lib-table $HOME/.config/kicad/9.0/ && '"$1"
}

# 1) schematic from tools/design.py (needs the KiCad symbol library files)
[ -d "$SYMDIR" ] || docker run --rm --user "$(id -u):$(id -g)" -v "$B:/b" "$IMG" cp -r /usr/share/kicad/symbols /b/
python3 "$HW/tools/gen_schematic.py" "$SYMDIR" "$HW/kicad/accessbridge.kicad_sch"
run "kicad-cli sch erc --severity-all --exit-code-violations -o /b/erc.rpt accessbridge.kicad_sch && kicad-cli sch export netlist -o /b/accessbridge.net accessbridge.kicad_sch"

# 2) placement + DSN export
run "python3 /w/tools/gen_pcb.py place /b/accessbridge.net accessbridge.kicad_pcb && python3 /w/tools/gen_pcb.py dsn accessbridge.kicad_pcb /b/accessbridge.dsn"

# 3) autorouting (single thread, optimizer disabled: see hardware/tools/README.md)
#    Freerouting is not deterministic. Set SES=<file> to reuse a known-good result.
if [ -n "${SES:-}" ]; then cp "$SES" "$B/accessbridge.ses"; else
mkdir -p "$B/fr"
cat > "$B/fr/freerouting.json" <<'JSON'
{"gui": {"enabled": false},
 "router": {"max_passes": 60, "max_threads": 1, "optimizer": {"max_passes": 0, "max_threads": 1}},
 "feature_flags": {"multi_threading": false},
 "profile": {"allow_telemetry": false, "allow_contact": false},
 "usage_and_diagnostic_data": {"disable_analytics": true}}
JSON
(cd "$B/fr" && timeout 900 java -Djava.awt.headless=true -Djava.io.tmpdir="$B/fr" -jar "$JAR" \
  -de "$B/accessbridge.dsn" -do "$B/accessbridge.ses" -mp 60 -mt 1 > "$B/freerouting.log" 2>&1 || true)
grep -o "score of [0-9.]* ([0-9]* unrouted)" "$B/freerouting.log" | tail -1
fi

# 4) import, clean up, pour, check
run "python3 /w/tools/gen_pcb.py ses accessbridge.kicad_pcb /b/accessbridge.ses"
run "python3 /w/tools/gen_pcb.py clean accessbridge.kicad_pcb"
run "python3 /w/tools/gen_pcb.py clean accessbridge.kicad_pcb"
run "python3 /w/tools/gen_pcb.py shift accessbridge.kicad_pcb"
run "python3 /w/tools/gen_pcb.py finish accessbridge.kicad_pcb"
run "kicad-cli pcb drc --severity-all --schematic-parity -o /b/drc.rpt accessbridge.kicad_pcb" || true
grep -E "Found" "$B/drc.rpt"
