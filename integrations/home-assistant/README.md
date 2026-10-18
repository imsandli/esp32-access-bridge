# Home Assistant

Two **blueprints** and one **example package**. They contain no hard-coded
entity IDs, IP addresses or credentials. You select the entities when you
create the automation.

| File | Type | Purpose |
|---|---|---|
| [automations/nuki-unlock.yaml](automations/nuki-unlock.yaml) | Automation blueprint | Unlatch/unlock the Nuki on a new, authorized UA-Hub pulse |
| [automations/doorbell-notify.yaml](automations/doorbell-notify.yaml) | Automation blueprint | Your notification actions on a new doorbell press |
| [examples/contact-monitoring.yaml](examples/contact-monitoring.yaml) | Package | Enable switch for unlatching, link-problem sensor and log entry |

Status: validated with Home Assistant **2026.2.3** (`check_config`) and covered
by 12 behaviour tests (see below). **Not tested with a real Nuki.**

## Install

1. Copy the two blueprint files to `<config>/blueprints/automation/accessbridge/`
   (or import them from their GitHub URLs in *Settings > Automations &
   scenes > Blueprints > Import*).
2. Optionally, copy `examples/contact-monitoring.yaml` to
   `<config>/packages/accessbridge.yaml` and adapt the entity IDs marked
   `substitute me`.
3. Create an automation from **"AccessBridge - open Nuki on authorized UA-Hub
   pulse"** and select:

| Input | Select |
|---|---|
| Relay pulse counter | the `relay_pulses` sensor from Zigbee2MQTT |
| Relay contact | the `relay_contact` binary sensor |
| Nuki lock | your Nuki `lock.*` entity (Nuki integration or Nuki via MQTT) |
| Lock action | `lock.open` (unlatch, default) or `lock.unlock` |
| Enable switch | optional, e.g. `input_boolean.accessbridge_unlatch_enabled` |
| Door closed sensor | optional, `door_closed` (DPS input mode) |
| Cooldown / freshness / verification | defaults 10 s / 15 s / 15 s |

## What the blueprint does NOT trust

* Never the contact state alone.
* Never a counter value restored after a restart (`unavailable`/`unknown`
  to a number).
* Never a counter decrease (device reboot) or a jump of more than 1.
* Never a pulse whose contact did not change within the freshness window
  (late delivery).

Details and trust boundaries: [docs/security.md](../../docs/security.md).

## Logging

* Logbook: every accepted pulse, every ignored pulse with its reason, and
  confirmed lock state changes.
* System log (`accessbridge` logger): warnings for stale pulses and counter
  jumps, **errors for unlatch commands that the lock did not confirm**.

## Tests

```sh
cd integrations/home-assistant
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements-test.txt
tests/check_config.sh      # Home Assistant's own config validation
pytest -q                  # 12 behaviour tests on a real HA core
```

The behaviour tests (`tests/test_blueprints.py`) cover: new pulse to unlatch
and confirmation, restored state, device reboot (and a pulse right after it),
counter jump, stale pulse, cooldown, enable switch, open door, unconfirmed
unlatch logged as an error, unlock-only mode, contact state alone, and the
doorbell (once per press, rate limit, restore).
