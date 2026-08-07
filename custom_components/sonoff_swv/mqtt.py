from __future__ import annotations

import json
import logging

from typing import TYPE_CHECKING, Any

from homeassistant.components import mqtt
from homeassistant.core import HomeAssistant

if TYPE_CHECKING:
    from .coordinator import SonoffSWVCoordinator


_LOGGER = logging.getLogger(__name__)



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

        _LOGGER.debug(
            "MQTT received: %s",
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
                "Invalid MQTT JSON received on %s"
                topic,
            )

            return


        _LOGGER.debug(
            "MQTT parsed payload: %s",
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