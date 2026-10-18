# Firmware tests

| Level | What | Where | Status |
|---|---|---|---|
| Static | `esphome config accessbridge.yaml`: schema, pins, Zigbee options | CI `firmware` workflow, locally | passing |
| Build | `esphome compile accessbridge.yaml` with ESPHome 2026.9.1 | CI `firmware` workflow | passing |
| Home Assistant side | Blueprint behaviour tests (counter rules, gates) | [`integrations/home-assistant/tests`](../../integrations/home-assistant/tests), CI `integrations` workflow | passing |
| On hardware | Debounce, short pulses, boot/rejoin behaviour, LED, PAIR button | Manual procedure: [docs/testing.md](../../docs/testing.md) (T-FW-*) | **not executed** |

There are no host-side unit tests of the ESPHome lambdas: ESPHome has no
supported way to run a configuration without the target. The counting logic
is kept small and is covered by the hardware tests T-FW-2 to T-FW-6.
