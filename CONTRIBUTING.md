# Contributing

Thank you for your interest in improving this integration. Contributions of any size are welcome: bug reports, captured device data, documentation, translations and code.

The project is maintained by one person, who reviews and merges every change. Please open an issue before starting a large change, so that the direction can be agreed first.

## License

By contributing you agree that your contribution is released under the **GNU General Public License v3.0**, the license of this project. You keep the copyright on what you write.

## Reporting a problem

Open an issue and include:

- the Home Assistant, Zigbee2MQTT and zigbee-herdsman-converters versions, and the firmware of the valve;
- what you did, what you expected and what happened;
- the relevant lines of the Home Assistant log;
- when it concerns the behaviour of the device, the **MQTT payloads** you captured (topic `zigbee2mqtt/<device>` and `zigbee2mqtt/<device>/set`), with the time of each line.

Please remove passwords and personal data from logs and payloads.

## Proposing a change

1. Fork the repository and create a branch from `main`.
2. Make a focused change: one subject per pull request.
3. Open a pull request against `main`, describing the problem and how you checked the result.

`main` is protected: every change goes through a pull request approved by the maintainer.

## Rules of the project

- **User-visible texts go in the catalog.** Messages, states, menu entries and summaries live in `custom_components/sonoff_swv/texts.py`, with an English and an Italian entry, and are read through the language of Home Assistant. Do not write sentences directly in the code. Attribute names used by dashboards are identifiers and stay fixed.
- **Device behaviour must come from data.** The device cannot be queried for its plans and Zigbee2MQTT republishes cached echoes of the last written settings, so a claim about what the device does needs captured payloads, not an assumption.
- **Composite settings are written as a whole group.** Recent Zigbee2MQTT and converters versions need the complete group in every write.
- **Draft fields do not write.** Plan, manual and seasonal fields change only the draft; the buttons write to the device.
- **Pure modules stay free of Home Assistant.** `irrigation_history.py`, `irrigation_plans.py` and `next_irrigation.py` have no Home Assistant imports, so their logic can be tested on its own.

## Checking your change

- Compile the files you touched: `python3 -m py_compile <file>`.
- Test pure modules from a folder **outside** `custom_components/sonoff_swv`, loading the file with `importlib`: files of the integration whose names match standard-library modules can shadow them when Python is started inside that folder.
- Restart Home Assistant and look at the log for errors from `sonoff_swv`.
- When you change a dashboard card, tell which entities it uses.

## Translations

Texts are in English and Italian. To add a language, add a block with the same keys as the English one in `texts.py`; missing keys fall back to English.
