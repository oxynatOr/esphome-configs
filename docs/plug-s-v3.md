# Shelly Plug S Gen3 (and the shared plug logic of the Plug M)

Packages for the **Shelly Plug S Gen3** (ESP32-C3, BL0942 energy meter, NTC, 4x WS2812 LED ring, one button, one relay).
This document was ported from the original `plug_s_gen3/README.md`; the protection, staggered restart, status logic and
add-ons are shared with the **Shelly Plug M Gen3**. Differences to the Plug M: the Plug M has a single RGB LED instead of the
ring and no usable button, so there are no gestures and no child lock - a latched fault is cleared by switching *Fault Lock*
off in Home Assistant.

**Core features**

- Latched protection against over-temperature, over-current and over-power, with inrush tolerance and a pre-warning
- Watchdog for the temperature sensor (an open or shorted NTC is detected)
- Button gestures: relay, effect selection, child lock (Plug S)
- Three live LED effects: current, power (logarithmic), temperature
- Staggered relay restart after a power loss

**Optional add-ons** (separate files, include only what you want)

- Night mode (LED dimming)
- Auto-off timer and standby killer
- Failsafe when Home Assistant is unreachable
- Diagnostics (last fault, fault counter, relay cycles)

> **Status:** `python scripts/check.py --esphome` passes and the full Plug S (all add-ons) and the full Plug M **compile** with
> ESPHome 2026.9.1. Nothing has been run on a device yet - check the gestures, the staggered restart (power loss and OTA)
> and the trip behaviour with a harmless load before relying on it.

---

## Files

| File | Purpose |
|---|---|
| `projects/plug-s/v3.yaml` | Adoptable device: ties everything below together |
| `hardware/plugs/plug-s/v3.yaml` | Hardware: board, relay, child-lock switch, LED ring, pins |
| `hardware/plugs/plug-s/button.yaml` | Button gestures |
| `hardware/plugs/plug-s/led-status.yaml` | LED effects and status signals |
| `hardware/plugs/common/relay-protection.yaml` | Protection, watchdog, staggered restart, Fault Lock |
| `hardware/plugs/common/status.yaml` | Wi-Fi / API / OTA status for the LEDs |
| `hardware/power-monitoring/bl0942.yaml`, `energy-counters.yaml` | Meter and energy sensors |
| `hardware/power-monitoring/bl0942-calibration.yaml` | Runtime calibration (number entities and buttons) |
| `hardware/plugs/addons/night.yaml` | Optional: night mode - manual switch and schedule |
| `hardware/plugs/addons/autooff.yaml` | Optional: auto-off timer and standby killer |
| `hardware/plugs/addons/failsafe.yaml` | Optional: what happens when Home Assistant is gone |
| `hardware/plugs/addons/diagnostics.yaml` | Optional: last fault, fault counter, relay cycles |

The add-ons only use ids defined in the core. Leave any of them out and the core works unchanged; nothing of it ends up in the firmware.

## Quick start

Device config in your ESPHome folder (repository cloned to `ioxys-esphome/`, or use `github://` references):

```yaml
substitutions:
  plug_relay_restore_mode: RESTORE_DEFAULT_ON   # relay state after power loss
  plug_led_restore_mode: RESTORE_DEFAULT_ON
  plug_max_temp: "70"        # trip above this temperature (C)
  plug_rearm_temp: "55"      # temperature fault clears automatically below this
  plug_max_current: "12"     # trip above this current (A), also LED bar full scale
  plug_max_power: "2800"     # trip above this power (W), also LED bar full scale
  plug_device_name: Freezer plug

packages:
  plug: !include ioxys-esphome/projects/plug-s/v3.yaml
  failsafe: !include ioxys-esphome/hardware/plugs/addons/failsafe.yaml   # optional, not part of the project
```

Entity names come from `i18n/en.yaml` (`txt_*` keys); override single texts with your own `substitutions:`.
The project already includes the night, auto-off and diagnostics add-ons (inert until you switch them on).

## Substitutions

### Device specific
| Name | Meaning |
|---|---|
| `plug_device_name` | Used in Home Assistant notifications |
| `plug_relay_restore_mode` | Relay state after a power loss (`RESTORE_DEFAULT_ON`, `RESTORE_DEFAULT_OFF`, `ALWAYS_ON`, `ALWAYS_OFF`, `RESTORE_INVERTED_DEFAULT_ON`, `RESTORE_INVERTED_DEFAULT_OFF`) |
| `plug_led_restore_mode` | Restore mode of the LED light |
| `ntc_update_interval`, `bl0942_update_interval` | Sensor update intervals |
| `plug_max_temp` | Trip above this temperature (C); also the red end of the temperature effect |
| `plug_rearm_temp` | A temperature fault clears automatically below this (C) |
| `plug_max_current` | Trip above this current (A); also full scale of the current bar |
| `plug_max_power` | Trip above this power (W); also full scale of the power bar |

The calibration references (`bl0942_voltage_reference`, `bl0942_current_reference`, `bl0942_power_reference`,
`bl0942_energy_reference`) default to the ESPHome values; calibrate with the runtime calibration entities and keep your
measured values in your own device config.

### Optional (defaults live in the package files)

| Name | Default | File | Meaning |
|---|---|---|---|
| `plug_warn_ratio` | `0.8` | core | Pre-warning starts at this fraction of `plug_max_temp` / `plug_max_current` / `plug_max_power` |
| `plug_trip_delay` | `500` | core | ms a current/power limit must stay exceeded before tripping |
| `plug_trip_delay_temp` | `3000` | core | ms the temperature limit must stay exceeded before tripping |
| `plug_trip_instant_factor` | `1.5` | core | Current/power above `limit × factor` trips immediately |
| `plug_power_bar_min` | `2` | core | W at the bottom of the logarithmic power bar |
| `plug_night_brightness` | `0.05` | core | LED brightness factor while night mode is active (`0` = LEDs off) |
| `plug_ntc_fault_trips` | `false` | core | `true`: a broken temperature sensor also switches the relay off. `false`: only warn |
| `plug_ntc_fail_delay` | `10000` | core | ms without a plausible temperature = sensor fault |
| `plug_startup_delay_min` | `0` | core | s, earliest relay-on after a power loss |
| `plug_startup_delay_max` | `10` | core | s, latest relay-on after a power loss |
| `plug_night_start` | `22` | night | Night window start (hour, 0–23) |
| `plug_night_end` | `6` | night | Night window end (hour, 0–23) |
| `plug_failsafe_action` | `KEEP` | failsafe | `KEEP`, `ON` or `OFF` |
| `plug_failsafe_timeout` | `10` | failsafe | Minutes without an API connection before the failsafe acts |

## Button gestures

| Gesture | Action |
|---|---|
| 1× click | Toggle relay (delayed by ~0.35 s, the plug waits for a possible second click) |
| 2× click | Next LED effect: Current → Power → Temperature |
| 3× click | Child lock **on** |
| 3× click, hold the last press 1.5 s | Child lock **off** |
| Hold 2.5 s | Acknowledge a fault; without a fault: LEDs on/off |

While the **child lock** is on, every press except the unlock gesture only flashes the LEDs orange. That includes acknowledging a fault by button – use the *Fault Lock* switch in Home Assistant then. Home Assistant control is not affected by the child lock. The lock survives power loss.

## LED signals

Highest priority first.

| Signal | Meaning |
|---|---|
| Orange blink (1.2 s) | Button pressed while the child lock is on |
| Fast red blink (3 s) | Button pressed while a fault is latched, or acknowledge refused because it is still too hot |
| Orange fill / green empty | Child lock engaged / released |
| Red breathing, all LEDs | Fault latched, relay is off |
| Magenta slow blink | Temperature sensor fault – the over-temperature protection is blind |
| Amber blink | Pre-warning: a value is at or above `plug_warn_ratio` of its limit |
| Red pulse on LED 0 | No Wi-Fi |
| Amber pulse, all LEDs | No API client (Home Assistant) connected |
| Blue runner | OTA update |
| **Effect** | Live Current / Live Power / Live Temperature (below) |
| Last LED breathes orange | Child lock is on (overlay on every effect) |

Night mode dims only the normal display (effect, Wi-Fi/API/OTA states). Faults, feedback and warnings are never dimmed.

### Effects

| Effect | Display |
|---|---|
| **Live Current** | Bar over the 4 LEDs, `0 … plug_max_current` (linear), green → red |
| **Live Power** | Bar, `plug_power_bar_min … plug_max_power` on a **logarithmic** scale, so standby (a few W) and full load (kW) are both readable |
| **Live Temperature** | Whole strip one colour: 25 °C blue → green → `plug_max_temp` red |

With the relay on and (almost) no load, LED 0 glows faintly in the bar effects.

## Protection

- **Debounce / inrush tolerance:** a current or power limit must stay exceeded for `plug_trip_delay` ms (temperature: `plug_trip_delay_temp`). A value above `limit × plug_trip_instant_factor` trips immediately. Measurements arrive every `bl0942_update_interval`, so with 1 s this effectively means two consecutive samples above the limit.
- **Latching:** a trip switches the relay off, turns on the *Fault Lock* switch and sends a persistent notification to Home Assistant. While the fault lock is on, the relay cannot be switched on (button or Home Assistant).
- **Acknowledge:** hold the button for 2.5 s (not possible while the child lock is on), or turn *Fault Lock* off in Home Assistant. A button acknowledge is refused while the temperature is still ≥ `plug_max_temp`.
- **Auto re-arm:** only the **over-temperature** fault clears by itself, once the temperature falls below `plug_rearm_temp`. Over-current and over-power stay latched (the current drops to 0 A after the relay opens, so an automatic re-arm would clear them at once).
- **Pre-warning:** at `plug_warn_ratio` (80 %) of any limit the LEDs blink amber; the warning is held for 1.5 s after the last sample above the level.

### Temperature sensor watchdog

If the temperature stays implausible (NaN, below −30 °C or above 130 °C, or no new value) for `plug_ntc_fail_delay` ms – an open, shorted or stalled NTC – the over-temperature protection cannot work. There is a 30 s grace period after boot. The plug then:

- blinks the LEDs magenta,
- turns on the *Temperature Sensor Fault* binary sensor in Home Assistant,
- sends a notification.

By default the relay **keeps its state** (`plug_ntc_fault_trips: "false"`), so a defective sensor does not switch off e.g. a freezer. With `plug_ntc_fault_trips: "true"` the relay is switched off and the fault latches; it clears automatically when readings are plausible again.

## Staggered restart

After a power loss the relay comes back after a random delay between `plug_startup_delay_min` and `plug_startup_delay_max` seconds, so that many plugs (or a plug and its load) do not switch on at the same instant. The relay state itself follows `plug_relay_restore_mode`, emulating the ESPHome restore modes.

- A **software reboot** (OTA update etc.) is detected and skips the delay.
- The relay GPIO switch uses `restore_mode: DISABLED`; the package switches it on after the delay. Relay changes made *during* the delay window are not remembered for the next boot.
- For compressor loads (freezer, fridge) use a longer window, e.g. `plug_startup_delay_min: "180"`, `plug_startup_delay_max: "300"`.

## Home Assistant entities

**Core**

| Entity | Type | Notes |
|---|---|---|
| Relay | switch | |
| Button Lock | switch | Child lock, persistent |
| Fault Lock | switch (diagnostic) | On = fault latched; turn off to acknowledge |
| Temperature Sensor Fault | binary sensor (problem) | NTC watchdog |
| LED | light | Effects: `Live Current`, `Live Power`, `Live Temperature` |
| Temperature, Voltage, Current, Power, Energy, Frequency, daily/total energy | sensors | |

**Night** (`hardware/plugs/addons/night.yaml`): *Night Mode*, *Night Mode Auto*.

**Auto-off** (`hardware/plugs/addons/autooff.yaml`): *Auto-Off Timer*, *Standby Killer*, *Standby Threshold*, *Standby Delay*.

**Diagnostics** (`hardware/plugs/addons/diagnostics.yaml`): *Last Fault*, *Fault Count*, *Relay Cycles*.

## Add-ons

### Night mode – `hardware/plugs/addons/night.yaml`

Dims the LED display to `plug_night_brightness` (default 5 %; `0` turns it off).

- **Night Mode** – manual switch (default off).
- **Night Mode Auto** – schedule `plug_night_start` … `plug_night_end` (default 22–6; wraps over midnight). Default on. Needs a synchronised clock (`time:`); without one the schedule does nothing.

Night mode is active if the manual switch is on **or** (auto is on and the time is inside the window).

### Auto-off timer and standby killer – `hardware/plugs/addons/autooff.yaml`

Both only ever switch the relay **off**, and both are disabled by default.

- **Auto-Off Timer** (minutes, 0 = off): the relay switches off this long after it was switched on. A restart of the plug restarts the countdown. Clock schedules such as "off at 22:00" belong in Home Assistant.
- **Standby Killer** (switch, default off): when on, and the power stays below **Standby Threshold** (W) for **Standby Delay** (minutes), the relay switches off and Home Assistant gets a notification.

> **Do not use the standby killer on compressor loads** (freezer, fridge). Their power is ~0 W while the compressor rests, so the plug would cut them off.

### Failsafe – `hardware/plugs/addons/failsafe.yaml`

Without this file the relay simply keeps its state when Home Assistant is gone. The ESPHome default reboot timeouts (15 min without API or Wi-Fi) however restart the device, which interrupts the relay for a moment. This file therefore sets `reboot_timeout: 0s` for `api` and `wifi`.

- `plug_failsafe_action: "KEEP"` (default): nothing happens, the relay never changes.
- `"ON"` / `"OFF"`: after `plug_failsafe_timeout` minutes without an API connection, the relay is switched on/off – **once per outage**, and only after Home Assistant has been back can it act again.
- A latched fault always wins; the failsafe never overrides the *Fault Lock*.

Typical use: a freezer plug that Home Assistant sometimes switches off – with `ON` it cannot stay off because Home Assistant died.

### Diagnostics – `hardware/plugs/addons/diagnostics.yaml`

- **Last Fault** – cause and time of the last latched fault (survives reboots; "clock unknown" if the clock was not synchronised).
- **Fault Count** – number of latched faults.
- **Relay Cycles** – how often the relay was switched on.

## Checklist for critical loads (freezer, server, …)

1. `plug_relay_restore_mode: RESTORE_DEFAULT_ON` (or `ALWAYS_ON`).
2. Consider `plug_startup_delay_min` / `plug_startup_delay_max` of 180 / 300 s for compressors.
3. Keep `plug_ntc_fault_trips: "false"` (default), so a broken sensor does not cut the load.
4. Include `hardware/plugs/addons/failsafe.yaml` with `plug_failsafe_action: "ON"`.
5. Do **not** include `hardware/plugs/addons/autooff.yaml` (or leave the timer at 0 and the standby killer off).
6. Set `plug_max_current` / `plug_max_power` above the real inrush and load of the device – a trip switches the load off until somebody acknowledges it.

## Hardware

| Function | Pin |
|---|---|
| Relay | GPIO4 |
| LED ring (4× WS2812) | GPIO5 |
| Button | GPIO18 |
| NTC (ADC) | GPIO3 |
| BL0942 UART TX / RX | GPIO7 / GPIO6 |

ESPHome prints a warning that GPIO18 is used by the USB-Serial-JTAG interface. It is the button pin of the plug; the warning is expected.

## Notes and known limitations

- If your ESPHome version rejects `channel_colors` on the LED strip, replace it with `rgb_order: GRB` in `hardware/plugs/plug-s/v3.yaml` (the combination with `channel_colors: GRB` compiled with ESPHome 2026.9.1).
- The effect names are English (`Live Current`, `Live Power`, `Live Temperature`). Automations using older German names need updating.
- The 1× click reacts ~0.35 s late because of the multi-click detection.
- `total_daily_energy` and the schedules need a `time:` component (the projects include `core/time-homeassistant.yaml`).
- Not tested on hardware: gestures, staggered restart (power loss and OTA) and the trip behaviour should be verified with a harmless load.
