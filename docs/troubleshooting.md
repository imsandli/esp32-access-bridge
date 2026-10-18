# Troubleshooting

| Symptom | Check |
|---|---|
| PWR LED off | 12 V at J1 1/2? Polarity (reversed input trips F1; it resets after power off)? LINE output really on (wiring.md)? |
| PWR LED on, status LED dark | XIAO plugged in the right way round (USB-C towards the board edge)? Firmware flashed? About 4.7 V at socket pin 14? |
| Status LED blinks fast forever | Not joined: permit join on in Z2M? Range (test T-Z2M-4)? Previously paired elsewhere: hold PAIR 5-15 s. |
| Joined, but no pulses | Relay in **dry** mode? Loop: about 3.3 mA with COM-NO shorted. Firmware log shows `UA-Hub relay contact CLOSED`? |
| Pulse in the log but "not counted" | `previous state unknown` (first change after boot): expected. `Zigbee not joined`: link problem. `within ... ms`: chatter or two quick accesses. |
| Counter increases but the Nuki does not open | HA logbook "AccessBridge": shows the reason (cooldown, disabled, door open, stale). System log `accessbridge`: errors from the lock. |
| HA logs "counter jumped" | Reports were lost (weak link). Check the link quality and the position of the coordinator/router. |
| HA logs "not closed within ... s" | Late delivery or a relay pulse shorter than the freshness window. Increase freshness slightly (it must remain shorter than any delay you consider unsafe). |
| Z2M shows strange property names after a firmware change | Remove the device, hold PAIR 5-15 s, re-pair (ESPHome requirement). |
| ESPHome boot loop after a config change | Erase flash: `esptool.py --chip esp32c6 erase_flash`, then flash again. |
| Serial port missing | Hold BOOT while plugging in USB-C; use a data cable. |
