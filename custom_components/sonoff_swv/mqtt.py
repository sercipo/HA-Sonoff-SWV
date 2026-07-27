from __future__ import annotations

import json

from homeassistant.components import mqtt


async def async_subscribe(hass, coordinator):

    topic = coordinator.topic_state

    @mqtt.callback
    def message_received(msg):

        try:
            payload = json.loads(msg.payload)
        except json.JSONDecodeError:
            return

        coordinator.update_from_device(payload)

    await mqtt.async_subscribe(
        hass,
        topic,
        message_received,
        0,
    )