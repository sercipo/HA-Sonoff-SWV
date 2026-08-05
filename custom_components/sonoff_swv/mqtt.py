from __future__ import annotations

import json
import logging

_LOGGER = logging.getLogger(__name__)

from typing import TYPE_CHECKING, Any

from homeassistant.components import mqtt
from homeassistant.core import HomeAssistant


if TYPE_CHECKING:

    from .coordinator import SonoffSWVCoordinator



async def async_subscribe(
    hass: HomeAssistant,
    coordinator: SonoffSWVCoordinator,
):
    """Subscribe to Zigbee2MQTT state topic."""


    topic = coordinator.topic_state



    @mqtt.callback
    def message_received(
        msg,
    ) -> None:

        _LOGGER.warning(
            "SONOFF MQTT RAW RECEIVED: %s",
            msg.payload,
        )

        try:

            payload: dict[str, Any] = json.loads(
                msg.payload
            )

        except (
            json.JSONDecodeError,
            TypeError,
        ):

            _LOGGER.warning(
                "SONOFF MQTT JSON ERROR"
            )

            return


        _LOGGER.warning(
            "SONOFF MQTT PARSED: %s",
            payload,
        )


        coordinator.update_from_device(
            payload
        )
        
    return await mqtt.async_subscribe(
        hass,
        topic,
        message_received,
        qos=0,
    )