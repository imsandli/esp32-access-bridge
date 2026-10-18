#!/usr/bin/env bash
# Shared helpers for the hardware scripts.
# Runs kicad-cli natively when KiCad 9 is installed, otherwise inside the
# pinned KiCad container (same image as CI).
set -euo pipefail

KICAD_IMAGE="${KICAD_IMAGE:-kicad/kicad:9.0.9}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HW="$REPO_ROOT/hardware"
KICAD_DIR="$HW/kicad"
PCB="$KICAD_DIR/accessbridge.kicad_pcb"
SCH="$KICAD_DIR/accessbridge.kicad_sch"
MFG="$HW/manufacturing"
HW_VERSION="HW-1.0"
PCB_REV="A"

# Global KiCad library tables are needed for library checks in a fresh
# environment (CI container, new user profile).
ensure_lib_tables() {
  local cfg="${HOME}/.config/kicad/9.0"
  if [ ! -f "$cfg/sym-lib-table" ] && [ -f /usr/share/kicad/template/sym-lib-table ]; then
    mkdir -p "$cfg"
    cp /usr/share/kicad/template/sym-lib-table /usr/share/kicad/template/fp-lib-table "$cfg/"
  fi
}

kicad_native() {
  command -v kicad-cli >/dev/null 2>&1 && kicad-cli version 2>/dev/null | grep -q '^9\.'
}

# kicad <args...>: run kicad-cli with paths relative to the repository root
kicad() {
  if kicad_native; then
    ensure_lib_tables
    (cd "$REPO_ROOT" && kicad-cli "$@")
  else
    docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp/home \
      -v "$REPO_ROOT:/repo" -w /repo "$KICAD_IMAGE" sh -c \
      'mkdir -p $HOME/.config/kicad/9.0 && cp /usr/share/kicad/template/*-lib-table $HOME/.config/kicad/9.0/ && kicad-cli "$@"' \
      kicad-cli "$@"
  fi
}

# kipython <script> <args...>: run a Python script that needs nothing but the stdlib
kipython() {
  if command -v python3 >/dev/null 2>&1; then
    (cd "$REPO_ROOT" && python3 "$@")
  else
    docker run --rm -v "$REPO_ROOT:/repo" -w /repo "$KICAD_IMAGE" python3 "$@"
  fi
}
