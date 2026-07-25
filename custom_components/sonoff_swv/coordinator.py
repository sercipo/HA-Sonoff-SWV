from __future__ import annotations

import json

from homeassistant.components import mqtt
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .device import Device
from .manual import ManualSettings
from .plan import Plan
from .storage import SonoffStorage


class SonoffSWVCoordinator(DataUpdateCoordinator):
    """Coordinator dell'integrazione."""

    def __init__(
        self,
        hass: HomeAssistant,
    ):

        super().__init__(
            hass,
            logger=None,
            name="Sonoff SWV",
        )

        self.storage = SonoffStorage(hass)

        self.device_name = "Sonoff_Irrigazione"

        self.topic_set = (
            f"zigbee2mqtt/{self.device_name}/set"
        )

        self.data = {}

        self.device: Device | None = None

        self.plan = Plan()

        self.manual = ManualSettings()

    async def async_initialize(self):

        self.data = await self.storage.load()

        plans = self.data.get(
            "plans",
            {},
        )

        plan_data = (
            plans.get("0")
            or plans.get(0)
        )

        if plan_data:

            self.plan = Plan.from_dict(
                plan_data
            )

        manual_data = self.data.get(
            "manual"
        )

        if manual_data:

            self.manual = ManualSettings.from_dict(
                manual_data
            )

    def update_from_device(
        self,
        payload: dict,
    ):

        self.data.update(payload)

        if "device" in payload:

            self.device = Device.from_dict(
                payload["device"]
            )

        if "irrigation_plan_settings" in payload:

            self.plan = Plan.from_dict(
                payload[
                    "irrigation_plan_settings"
                ]
            )

            self.data.setdefault(
                "plans",
                {}
            )

            self.data["plans"]["0"] = (
                self.plan.to_dict()
            )

        if "manual_default_settings" in payload:

            self.manual = ManualSettings.from_dict(
                payload[
                    "manual_default_settings"
                ]
            )

            self.data["manual"] = (
                self.manual.to_dict()
            )

        self.async_set_updated_data(
            self.data
        )

    async def publish_plan(self):

        payload = {
            "irrigation_plan_settings":
                self.plan.to_dict()
        }

        await mqtt.async_publish(
            self.hass,
            self.topic_set,
            json.dumps(payload),
            qos=0,
            retain=False,
        )

        self.data.setdefault(
            "plans",
            {}
        )

        self.data["plans"]["0"] = (
            self.plan.to_dict()
        )

        await self.async_save()

        self.async_set_updated_data(
            self.data
        )

    async def publish_manual(self):

        payload = {
            "manual_default_settings":
                self.manual.to_dict()
        }

        await mqtt.async_publish(
            self.hass,
            self.topic_set,
            json.dumps(payload),
            qos=0,
            retain=False,
        )

        self.data["manual"] = (
            self.manual.to_dict()
        )

        await self.async_save()

        self.async_set_updated_data(
            self.data
        )

    def get_object(
        self,
        object_name: str,
    ):

        return getattr(
            self,
            object_name,
        )
    
    async def async_save(self):

        await self.storage.save(
            self.data
        )