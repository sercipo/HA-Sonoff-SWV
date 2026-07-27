from __future__ import annotations

import json

from homeassistant.components import mqtt
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)

from .models.device import Device
from .storage import SonoffStorage
from .mqtt import async_subscribe


class SonoffSWVCoordinator(DataUpdateCoordinator):
    """Coordinator dell'integrazione."""

    def __init__(
        self,
        hass: HomeAssistant,
        device_name: str,
    ):

        super().__init__(
            hass,
            logger=None,
            name="Sonoff SWV",
        )

        self.storage = SonoffStorage(hass)

        self.data: dict[str, object] = {}

        self.device_name = device_name

        self.topic_state = (
            f"zigbee2mqtt/{self.device_name}"
        )

        self.topic_set = (
            f"zigbee2mqtt/{self.device_name}/set"
        )

        self.device = Device()

    async def async_initialize(self):

        self.data = await self.storage.load()

        device = self.data.get(
            "device",
            {},
        )

        if device:

            self.device = Device.from_dict(
                device
            )

        else:

            self.device = Device()

    def update_from_device(
        self,
        payload: dict,
    ) -> None:

        self.data.setdefault(
            "device",
            {},
        )

        self.data["device"].update(
            payload
        )

        self.device.update_from_dict(
            self.data["device"]
        )

        self.async_set_updated_data(
            self.data
        )

    async def publish_plan(self):

        payload = {
            "irrigation_plan_settings":
                self.device.plan.to_dict()
        }

        await mqtt.async_publish(
            self.hass,
            self.topic_set,
            json.dumps(payload),
            qos=0,
            retain=False,
        )

        self.data.setdefault(
            "device",
            {},
        )

        self.data["device"][
            "irrigation_plan_settings"
        ] = self.device.plan.to_dict()

        await self.async_save()

        self.async_set_updated_data(
            self.data
        )

    async def publish_manual(self):

        payload = {
            "manual_default_settings":
                self.device.manual.to_dict()
        }

        await mqtt.async_publish(
            self.hass,
            self.topic_set,
            json.dumps(payload),
            qos=0,
            retain=False,
        )

        self.data.setdefault(
            "device",
            {},
        )

        self.data["device"][
            "manual_default_settings"
        ] = self.device.manual.to_dict()

        await self.async_save()

        self.async_set_updated_data(
            self.data
        )

    async def async_save(self):

        await self.storage.save(
            self.data
        )

    async def async_start(self):

        self._unsubscribe = await async_subscribe(
            self.hass,
            self,
        )

    async def async_stop(self):

        if hasattr(
            self,
            "_unsubscribe",
        ):

            self._unsubscribe()