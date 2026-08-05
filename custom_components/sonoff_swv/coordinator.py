from __future__ import annotations

import json
import logging
from typing import Any

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


_LOGGER = logging.getLogger(__name__)


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
            _LOGGER,
            name="Sonoff SWV",
        )


        self.hass = hass

        self.storage = SonoffStorage(
            hass,
        )

        self.device_name = device_name


        self.topic_state = (
            f"zigbee2mqtt/{device_name}"
        )

        self.topic_set = (
            f"zigbee2mqtt/{device_name}/set"
        )


        self.data: dict[str, Any] = {}

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
        payload: dict[str, Any],
    ) -> None:
        """Update Device from Zigbee2MQTT payload."""

        self.logger.warning(
            "SONOFF PAYLOAD: %s",
            payload,
        )

        self._update_device_from_payload(
            payload
        )

        self.logger.warning(
            "DEVICE MODEL: %s",
            self.device,
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


    def _update_device_from_payload(
        self,
        payload: dict[str, Any],
    ) -> None:
        """Normalize Zigbee2MQTT payload into flat Device model."""


        #
        # Simple flat attributes
        #

        for key, value in payload.items():

            if hasattr(
                self.device,
                key,
            ):

                setattr(
                    self.device,
                    key,
                    value,
                )



        #
        # Manual default settings
        #

        manual = payload.get(
            "manual_default_settings",
            {},
        )


        if manual:

            self.device.manual_default_settings = manual


            self.device.manual_irrigation_amount = (
                manual.get("irrigation_amount")
            )

            self.device.manual_irrigation_amount_unit = (
                manual.get("irrigation_amount_unit")
            )

            self.device.manual_irrigation_mode = (
                manual.get("irrigation_mode")
            )

            self.device.manual_irrigation_duration = (
                manual.get("irrigation_duration")
            )

            self.device.manual_irrigation_total_duration = (
                manual.get("irrigation_total_duration")
            )

            self.device.manual_interval_duration = (
                manual.get("interval_duration")
            )

            self.device.manual_fail_safe = (
                manual.get("fail_safe")
            )



        #
        # Irrigation plan settings
        #

        plan = payload.get(
            "irrigation_plan_settings",
            {},
        )


        if plan:

            self.device.irrigation_plan_settings = plan


            self.device.irrigation_plan_amount = (
                plan.get("irrigation_amount")
            )

            self.device.irrigation_plan_amount_unit = (
                plan.get("irrigation_amount_unit")
            )

            self.device.irrigation_plan_mode = (
                plan.get("irrigation_mode")
            )

            self.device.irrigation_plan_duration = (
                plan.get("irrigation_duration")
            )

            self.device.irrigation_plan_total_duration = (
                plan.get("irrigation_total_duration")
            )

            self.device.irrigation_plan_interval_duration = (
                plan.get("interval_duration")
            )

            self.device.irrigation_plan_interval_days = (
                plan.get("loop_type_interval_days")
            )

            self.device.irrigation_plan_start_time = (
                plan.get("start_time")
            )

            self.device.irrigation_plan_fail_safe = (
                plan.get("fail_safe")
            )



        #
        # Valve alarm settings
        #

        alarm = payload.get(
            "valve_alarm_settings",
            {},
        )


        if alarm:

            self.device.valve_alarm_settings = alarm


            self.device.enable_alarm_water_shortage = (
                alarm.get("enable_alarm_water_shortage")
            )

            self.device.enable_alarm_water_leak = (
                alarm.get("enable_alarm_water_leak")
            )

            self.device.enable_water_shortage_auto_close = (
                alarm.get("enable_water_shortage_auto_close")
            )

            self.device.enable_water_leak_auto_close = (
                alarm.get("enable_water_leak_auto_close")
            )

            self.device.enable_frost_protection = (
                alarm.get("enable_frost_protection")
            )

            self.device.set_frost_temperature = (
                alarm.get("set_frost_temperature")
            )

            self.device.alarm_water_leak_duration = (
                alarm.get("alarm_water_leak_duration")
            )

            self.device.alarm_water_shortage_duration = (
                alarm.get("alarm_water_shortage_duration")
            )



        #
        # Weather adjustment
        #

        weather = payload.get(
            "weather_based_adjustment",
            {},
        )


        if weather:

            self.device.weather_based_adjustment = weather



        #
        # Seasonal adjustment
        #

        seasonal = payload.get(
            "seasonal_watering_adjustment",
            {},
        )


        if seasonal:

            self.device.seasonal_watering_adjustment = seasonal



        #
        # Records
        #

        self.device.records_24_hours = (
            payload.get("24_hours_records")
        )

        self.device.records_30_days = (
            payload.get("30_days_records")
        )

        self.device.records_180_days = (
            payload.get("180_days_records")
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
        payload: dict[str, Any] | None = None,
    ) -> None:
        """Publish MQTT command."""


        mqtt_payload = {
            command: payload or {},
        }


        await mqtt.async_publish(
            self.hass,
            self.topic_set,
            json.dumps(
                mqtt_payload
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