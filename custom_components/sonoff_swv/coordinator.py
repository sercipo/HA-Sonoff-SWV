from __future__ import annotations

import json
import logging

from homeassistant.components import mqtt
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)

from .mapper import (
    build_payload_for_attribute,
)
from .models.device import Device
from .mqtt import async_subscribe
from .storage import SonoffStorage


class SonoffSWVCoordinator(
    DataUpdateCoordinator,
):
    """Coordinator for Sonoff SWV integration."""


    def __init__(
        self,
        hass: HomeAssistant,
        device_name: str,
    ) -> None:

        super().__init__(
            hass,
            logging.getLogger(__name__),
            name="Sonoff SWV",
        )

        self.storage = SonoffStorage(
            hass
        )

        self.device_name = device_name
        self.hass = hass

        self.topic_state = (
            f"zigbee2mqtt/{device_name}"
        )

        self.topic_set = (
            f"zigbee2mqtt/{device_name}/set"
        )

        self.data: dict = {}

        self.device = Device()



    async def async_initialize(
        self,
    ) -> None:
        """Load stored data."""

        self.data = await self.storage.load()


        stored_device = self.data.get(
            "device",
            {},
        )


        if stored_device:

            self.device = (
                Device.from_storage_dict(
                    stored_device
                )
            )


        self.async_set_updated_data(
            self.data
        )



    def update_from_device(
        self,
        payload: dict,
    ) -> None:
        """Update device from MQTT payload."""

        self.device.update_from_z2m_payload(
            payload
        )


        self.data[
            "device"
        ] = self.device.to_storage_dict()


        self.async_set_updated_data(
            self.data
        )


        self.hass.async_create_task(
            self.async_save()
        )



    async def publish_attribute(
        self,
        attribute: str,
    ) -> None:
        """Publish changed Device attribute."""

        payload = build_payload_for_attribute(
            self.device,
            attribute,
        )


        if not payload:

            return


        await mqtt.async_publish(
            self.hass,
            self.topic_set,
            json.dumps(
                payload
            ),
            qos=0,
            retain=False,
        )


        self.data[
            "device"
        ] = self.device.to_storage_dict()


        await self.async_save()


        self.async_set_updated_data(
            self.data
        )



    async def publish_command(
        self,
        command: str,
    ) -> None:
        """Publish MQTT command."""

        payload = {
            command: {},
        }


        await mqtt.async_publish(
            self.hass,
            self.topic_set,
            json.dumps(
                payload
            ),
            qos=0,
            retain=False,
        )



    async def async_save(
        self,
    ) -> None:
        """Save local storage."""

        await self.storage.save(
            self.data
        )



    async def async_start(
        self,
    ) -> None:
        """Start MQTT listener."""

        self._unsubscribe = await async_subscribe(
            self.hass,
            self,
        )



    async def async_stop(
        self,
    ) -> None:
        """Stop MQTT listener."""

        if hasattr(
            self,
            "_unsubscribe",
        ):

            self._unsubscribe()