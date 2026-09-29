from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import (
    AddEntitiesCallback,
)

from .const import DOMAIN
from .coordinator import SonoffSWVCoordinator
from .entity import SonoffSWVEntity
from .entity_resolver import find_mqtt_entity
from .entity_resolver import mqtt_entity_exists
from .entity_setup import async_add_entities_after_start
from .irrigation_history import (
    daily_series,
    sum_last_days,
    summarize_last_event,
)



@dataclass(frozen=True)
class SonoffSWVSensorDescription(
    SensorEntityDescription,
):
    """Description for Sonoff SWV sensors."""


SENSORS = (
    SonoffSWVSensorDescription(
        key="battery",
        name="Battery",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
    ),
    SonoffSWVSensorDescription(
        key="linkquality",
        name="Link quality",
    ),
    # SonoffSWVSensorDescription(
    #     key="irrigation_plan_amount",
    #     name="Irrigation plan amount",
    #     native_unit_of_measurement="L",
    # ),
    # SonoffSWVSensorDescription(
    #     key="manual_irrigation_amount",
    #     name="Manual irrigation amount",
    #     native_unit_of_measurement="L",
    # ),
    SonoffSWVSensorDescription(
        key="real_time_irrigation_volume",
        name="Real time irrigation volume",
        native_unit_of_measurement="L",
    ),
    SonoffSWVSensorDescription(
        key="real_time_irrigation_duration",
        name="Real time irrigation duration",
        native_unit_of_measurement="min",
    ),
    SonoffSWVSensorDescription(
        key="daily_irrigation_volume",
        name="Daily irrigation volume",
        native_unit_of_measurement="L",
    ),
    SonoffSWVSensorDescription(
        key="daily_irrigation_duration",
        name="Daily irrigation duration",
        native_unit_of_measurement="min",
    ),
    SonoffSWVSensorDescription(
        key="hour_irrigation_volume",
        name="Hour irrigation volume",
        native_unit_of_measurement="L",
    ),
    SonoffSWVSensorDescription(
        key="hour_irrigation_duration",
        name="Hour irrigation duration",
        native_unit_of_measurement="min",
    ),
    SonoffSWVSensorDescription(
        key="rain_delay",
        name="Rain delay",
    ),
    SonoffSWVSensorDescription(
        key="irrigation_schedule_status",
        name="Irrigation schedule status",
    ),
    SonoffSWVSensorDescription(
        key="valve_abnormal_state",
        name="Valve abnormal state",
    ),
    SonoffSWVSensorDescription(
        key="irrigation_plan_report",
        name="Irrigation plan report",
    ),
    SonoffSWVSensorDescription(
        key="irrigation_last_event",
        name="Irrigation last event",
    ),
    SonoffSWVSensorDescription(
        key="irrigation_volume_30d",
        name="Irrigation volume 30 days",
        native_unit_of_measurement="L",
    ),
    SonoffSWVSensorDescription(
        key="irrigation_history_chart",
        name="Irrigation history chart",
    ),
    # SonoffSWVSensorDescription(
    #     key="irrigation_plan_duration",
    #     name="Irrigation plan duration",
    #     native_unit_of_measurement="min",
    # ),
#   SonoffSWVSensorDescription(
#         key="irrigation_plan_total_duration",
#         name="Irrigation plan total duration",
#         native_unit_of_measurement="min",
#     ),  
    # SonoffSWVSensorDescription(
    #     key="irrigation_plan_interval_days",
    #     name="Irrigation plan interval days",
    # ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sonoff SWV sensors."""

    coordinator: SonoffSWVCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities_after_start(
        hass,
        async_add_entities,
        coordinator,
        SENSORS,
        SonoffSWVSensor,
        "sensor",
    )

class SonoffSWVSensor(
    SonoffSWVEntity,
    SensorEntity,
):
    """Sonoff SWV sensor entity."""

    entity_description: SonoffSWVSensorDescription

    def __init__(
        self,
        coordinator: SonoffSWVCoordinator,
        description: SonoffSWVSensorDescription,
    ) -> None:

        super().__init__(coordinator)

        self.entity_description = description

    @property
    def native_value(
        self,
    ):

        key = self.entity_description.key

        if key == "irrigation_schedule_status":

            value = self.get_value()

            if not isinstance(value, dict):
                return None

            return value.get("schedule_status")

        if key == "irrigation_plan_report":

            value = self.get_value()

            if value:
                return "available"

            return None

        if key == "irrigation_last_event":

            history = self.coordinator.data.get(
                "irrigation_history",
                [],
            )

            last_event = summarize_last_event(history)

            if last_event is None:
                return None

            return last_event.get("end_time")

        if key == "irrigation_volume_30d":

            history = self.coordinator.data.get(
                "irrigation_history",
                [],
            )

            return sum_last_days(
                history,
                days=30,
            )

        if key == "irrigation_history_chart":

            # This entity only carries data via extra_state_attributes;
            # the state itself is not meaningful on its own.
            return "available"

        return self.get_value()

    @property
    def extra_state_attributes(
        self,
    ):

        key = self.entity_description.key

        if key in (
            "irrigation_schedule_status",
            "irrigation_plan_report",
        ):

            value = self.get_value()

            if not isinstance(
                value,
                dict,
            ):

                return None

            return value

        if key == "irrigation_last_event":

            history = self.coordinator.data.get(
                "irrigation_history",
                [],
            )

            return summarize_last_event(history)

        if key == "irrigation_history_chart":

            history = self.coordinator.data.get(
                "irrigation_history",
                [],
            )

            return daily_series(
                history,
                days=10,
            )

        return None