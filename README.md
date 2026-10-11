# Sonoff SWV-ZFE for Home Assistant

Custom integration for the **SONOFF SWV-ZFE** Zigbee smart water valve (with flow meter), used through **Zigbee2MQTT**.

It does not replace the entities that Zigbee2MQTT already creates. It adds a logical layer on top of them:

- it **reuses the MQTT entities** whenever they represent a value of the device, without duplicating them;
- it **creates its own entities** only for what MQTT does not expose (composite settings, commands, local settings of the integration);
- it manages the irrigation plans, keeps a local history of the irrigations, calculates the next one and sends notifications.

> **Unofficial project.** It is not affiliated with SONOFF or eWeLink. Use it at your own risk: a wrong plan can open a water valve.

## Features

- **Irrigation plans** (6 slots, index 0-5): create, save and remove plans from Home Assistant, with a persistent local archive of what was written.
- **Next irrigation** sensor with the planned start, end and quantity, plus a warning when the device announces something different from what the archive expects.
- **Manual irrigation** start and stop, in duration or quantity mode.
- **Irrigation history** per session (planned and manual), stored locally for 90 days, with last event, 30-day volume and chart data.
- **Notifications** to Telegram or to the Home Assistant companion app: advance warning, plan start and end, valve open and closed, water shortage and water leak alarms, low battery with an adjustable threshold.
- **Alarm settings**: water leak and water shortage alarms, their durations, automatic closing, child lock.
- **Seasonal watering adjustment**: twelve monthly multipliers (0.1-2.0), edited as a draft and written with one button, plus a reset to 1.0.
- **Rain delay**: pause the schedules for a number of hours, with a status indicator.

## Requirements

- Home Assistant with the **MQTT** integration connected to the broker used by Zigbee2MQTT.
- **Zigbee2MQTT** publishing the SWV-ZFE.
- For the notifications: the **Telegram bot** integration with its `notify` entities, or the **mobile app** (companion app) `notify` entities.

### Tested with

| Component | Version |
|---|---|
| Home Assistant Core | 2026.9.2 (container) |
| Zigbee2MQTT | 2.14.1 |
| zigbee-herdsman-converters | 26.105.0 |
| SWV-ZFE firmware | 1.1.0 |

Tested with **a single valve**. The behaviour of several valves in the same Home Assistant is not supported yet.

With Zigbee2MQTT 2.13.0 / converters 26.90.0 or newer the converter groups several settings in composite fields that must be written as a whole. The integration always sends the complete group, so single changes do not leave the device with partial values.

## Installation

### HACS (custom repository)

1. In HACS open the menu and choose **Custom repositories**.
2. Add `https://github.com/sercipo/HA-Sonoff-SWV` with category **Integration**.
3. Install **Sonoff SWV** and restart Home Assistant.

### Manual

Copy the folder `custom_components/sonoff_swv` of this repository into the `custom_components` folder of your Home Assistant configuration, then restart.

## Setup

1. Go to **Settings → Devices & services → Add integration** and search for **Sonoff SWV**.
2. In the **Sonoff SWV device** field select the SWV-ZFE as registered by Zigbee2MQTT / MQTT. The IEEE address is extracted automatically and used to link the existing MQTT entities.
3. Confirm. A device can be configured only once; if it does not appear or is refused, check that it is a Zigbee2MQTT device known to the MQTT integration.

The device must already be known to Zigbee2MQTT and to the MQTT integration. The IEEE address is read from the device registry once, at configuration time.

## Entities

Entity ids start with the name of the device in Zigbee2MQTT. In the examples below the device is called `Sonoff_Irrigazione`, so the entities are `…sonoff_irrigazione_…`.

| Platform | What it is |
|---|---|
| `number` | Plan fields (index, quantity, durations, interval days, fail-safe), manual fields, alarm durations, 12 seasonal multipliers, rain delay hours, battery notification threshold |
| `select` | Plan mode and repetition, manual mode, history period, notification type, recipient and advance-warning minutes |
| `switch` | Plan enabled, the 7 weekdays, water leak and water shortage alarms, automatic closing, notification switches |
| `time`, `date` | Plan start time and start date |
| `button` | Save plan, remove plan, remove all plans, start and stop manual irrigation, read history, save and reset seasonal adjustment, set and cancel rain delay |
| `text` | Name used in the notification messages |
| `sensor` | Next irrigation, last irrigation, plans summary, 30-day volume, history chart, rain delay status and detail |

Values that Zigbee2MQTT already exposes (valve on/off, battery, link quality, child lock, counters) are used from the MQTT entities and are not duplicated.

## How it works

### Plans and drafts

The fields of a plan, of the manual irrigation and of the seasonal adjustment are a **draft**: changing a field writes nothing. Only the buttons write to the device (**Save plan**, **Start manual irrigation**, **Save seasonal adjustment**). Selecting a plan index loads the archived plan into the form, or default values if the plan is not known.

Defaults for a new plan: disabled, every 1 day, start at 06:00, quantity mode, 1 litre, fail-safe 10 minutes.

### Plan modes

| Mode | Where | Meaning |
|---|---|---|
| `duration` | plans and manual | the irrigation lasts the **total duration** |
| `capacity` | plans and manual | the irrigation stops when the **quantity** is delivered, or when the **fail-safe** time expires |
| `duration_with_interval` | plans only | cycles with pauses: the **total duration** is the whole window, pauses included, **cycle duration** is each opening and **interval** is the pause between cycles |

The fail-safe only matters in `capacity` mode: in the duration modes the device ignores it, so the card hides it there. Quantities are whole litres (resolution 1 L). The history records the **measured** quantity, not the planned one.

### Important limits of the device

- **The device cannot be queried for its plans.** The integration knows only what it wrote itself (and the report that the device publishes now and then). A plan changed from Zigbee2MQTT or from the SONOFF app is **not seen**: for the full management, plans must be set from this integration.
- The warning *plans not aligned* compares the next run announced by the device with the one calculated from the archive. It is a hint, not a proof.
- The **repetition interval in days must be at least 1**. The device silently discards a plan with 0 days: the plan looks saved but never runs.
- The device is battery powered (end device): some reports arrive with a delay.
- Zigbee2MQTT republishes the last written settings as a cached echo. The integration deliberately ignores this echo, because it is not a reading of the device.

### Notifications

Set the **notification type** (Telegram or companion app), then the **recipient**. All other options stay disabled until a recipient is chosen. Every message starts with the name of the device in square brackets; the name can be changed in the **device label** field (empty = name from Zigbee2MQTT). The texts (messages, menu entries and summaries) follow the **system language** of Home Assistant: English and Italian are available, other languages fall back to English.

- Messages about plans (advance warning, start, end) are sent only for **scheduled** irrigations, once per event, and never for events older than 10 minutes.
- **Valve open / closed** always follows the state of the valve, unless the plan notifications are on: in that case a scheduled irrigation is announced by the plan messages only, and the valve messages are not repeated.
- The **advance warning** is a single timer set at the start of the next irrigation minus the chosen minutes; it is recalculated when plans or settings change. A plan changed outside the integration is not seen.
- **Water shortage**: with *automatic closing on shortage* enabled the device closes the valve without reporting the alarm, so no notification is possible. The alarm message is sent when the automatic closing is off.
- **Low battery**: one message when the battery level drops to the chosen threshold (5-50%, default 20%). The warning is armed again when the level rises more than 5 points above the threshold. Zigbee2MQTT reports the battery only now and then, so the message can arrive some hours after the real event.

### Water shortage and low flow

A low flow can be interpreted by the valve as a lack of water. With the automatic closing enabled, every irrigation longer than the **shortage alarm duration** is cut. Set that duration (1-10 minutes) above the longest irrigation you plan, or disable the automatic closing.

### Seasonal adjustment

Twelve multipliers, one per month (1.0 = 100%). The values are a local draft that starts at 1.0 and is **not read from the device**: **Save** writes all twelve months at once, **Reset** puts all of them back to 1.0 and writes them.

### Rain delay

Choose the number of hours and press **Set rain delay**: the integration sends the end time to the device. **Cancel** sends `0`. The status indicator shows *Active* with the setting time and goes back to *Inactive* when the delay expires. It tracks only the delays set from the integration.

## Dashboard

The entities can be arranged freely. An example dashboard (plans, manual irrigation, alarms, notifications, seasonal adjustment and rain delay) is planned in the `examples` folder. **[TODO: add `examples/dashboard.yaml`.]**

The `apexcharts-card` chart of the history uses the attributes `days`, `automatic_liters` and `manual_liters` of the history chart sensor.

## Troubleshooting

- **A saved plan never runs.** Check the interval in days (at least 1) and that *Plan enabled* is on. Remember that the device gives no error for an invalid plan.
- **The irrigation stops too early.** With low flow, check the water shortage alarm duration and the automatic closing; in `capacity` mode check the fail-safe.
- **The notification options are greyed out.** Choose the notification type and then the recipient.
- **A plan changed elsewhere is not in the cards.** Write it again from the integration.

## Reporting problems

Open an issue at <https://github.com/sercipo/HA-Sonoff-SWV/issues> with the Home Assistant, Zigbee2MQTT and converters versions and the relevant lines of the log.

## Contributing

Contributions are welcome through pull requests: see [CONTRIBUTING.md](CONTRIBUTING.md). The maintainer reviews and merges the changes. By contributing you agree that your contribution is released under the license of the project.

## License

This project is licensed under the **GNU General Public License v3.0**, see the [LICENSE](LICENSE) file. In short: you can use, study and modify it freely; if you distribute a modified version you must release it, with its source code, under the same license.
