from __future__ import annotations

import json

from homeassistant.components import mqtt
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)

from .models.alarm import AlarmSettings
from .models.device import Device
from .models.manual import ManualSettings
from .models.plan import Plan
from .models.seasonal import SeasonalSettings
from .models.weather import WeatherSettings
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

        self.topic_set = (
            f"zigbee2mqtt/{self.device_name}/set"
        )

        self.device: Device | None = None

        self.plan = Plan()

        self.manual = ManualSettings()

        self.weather = WeatherSettings()

        self.seasonal = SeasonalSettings()

        self.alarm = AlarmSettings()

    async def async_initialize(self):

        self.data = await self.storage.load()

        user = self.data.get(
            "user",
            {},
        )

        device = self.data.get(
            "device",
            {}
        )

        if device:

            self.device = Device.from_dict(
                device
            )
        if "plan" in user:
            self.plan = Plan.from_dict(
                user["plan"]
            )

        if "manual" in user:
            self.manual = ManualSettings.from_dict(
                user["manual"]
            )

        if "weather" in user:
            self.weather = WeatherSettings.from_dict(
                user["weather"]
            )

        if "seasonal" in user:
            self.seasonal = SeasonalSettings.from_dict(
                user["seasonal"]
            )

        if "alarm" in user:
            self.alarm = AlarmSettings.from_dict(
                user["alarm"]
            )

    def update_from_device(
        self,
        payload: dict,
    ) -> None:

        self.data.setdefault(
            "device",
            {}
        )

        self.data.setdefault(
            "user",
            {}
        )

        if "device" in payload:

            self.device = Device.from_dict(
                payload["device"]
            )

            self.data["device"] = (
                self.device.to_dict()
            )

        if "irrigation_plan_settings" in payload:

            self.plan = Plan.from_dict(
                payload["irrigation_plan_settings"]
            )

            self.data["user"]["plan"] = (
                self.plan.to_dict()
            )

        if "manual_default_settings" in payload:

            self.manual = ManualSettings.from_dict(
                payload["manual_default_settings"]
            )

            self.data["user"]["manual"] = (
                self.manual.to_dict()
            )

        if "weather_based_adjustment" in payload:

            self.weather = WeatherSettings.from_dict(
                payload["weather_based_adjustment"]
            )

            self.data["user"]["weather"] = (
                self.weather.to_dict()
            )

        if "seasonal_watering_adjustment" in payload:

            self.seasonal = SeasonalSettings.from_dict(
                payload["seasonal_watering_adjustment"]
            )

            self.data["user"]["seasonal"] = (
                self.seasonal.to_dict()
            )

        if "valve_alarm_settings" in payload:

            self.alarm = AlarmSettings.from_dict(
                payload["valve_alarm_settings"]
            )

            self.data["user"]["alarm"] = (
                self.alarm.to_dict()
            )

        self.async_set_updated_data(
            self.data
        )

        self.hass.async_create_task(
            self.async_save()
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
            "user",
            {}
        )

        self.data["user"]["plan"] = (
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

        self.data.setdefault(
            "user",
            {}
        )

        self.data["user"]["manual"] = (
            self.manual.to_dict()
        )

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
    
    def get_object(
        self,
        object_name: str,
    ):

        return getattr(
            self,
            object_name,
        )