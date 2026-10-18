#!/usr/bin/env bash
# Validate the blueprints and the example package with Home Assistant's own
# config checker (hass --script check_config). Requires `hass` on PATH.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
CFG="$(mktemp -d)"
trap 'rm -rf "$CFG"' EXIT
mkdir -p "$CFG/blueprints/automation/accessbridge" "$CFG/packages"
cp "$HERE"/../automations/*.yaml "$CFG/blueprints/automation/accessbridge/"
cp "$HERE/../examples/contact-monitoring.yaml" "$CFG/packages/accessbridge.yaml"
cp "$HERE/check_config/configuration.yaml" "$CFG/configuration.yaml"
OUT="$(hass --script check_config -c "$CFG" 2>&1 || true)"
echo "$OUT" | grep -v '^INFO'
if echo "$OUT" | grep -q -E "Failed config|ERROR|Invalid config"; then
  echo "check_config FAILED"; exit 1
fi
echo "OK: Home Assistant check_config passed"
