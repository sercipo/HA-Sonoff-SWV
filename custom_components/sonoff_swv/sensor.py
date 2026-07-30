from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
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


@dataclass(frozen=True)
class SonoffSWVSensorDescription(
    SensorEntityDescription,
):
    """Description for Sonoff SWV sensors."""



SENSORS = (

    SonoffSWVSensorDescription(
        key="battery",
        name="Battery",
        native_unit_of_measurement=PERCENTAGE,
    ),


    SonoffSWVSensorDescription(
        key="linkquality",
        name="Link quality",
        native_unit_of_measurement="lqi",
    ),


    SonoffSWVSensorDescription(
        key="irrigation_plan_amount",
        name="Irrigation plan amount",
        native_unit_of_measurement="L",
    ),


    SonoffSWVSensorDescription(
        key="manual_irrigation_amount",
        name="Manual irrigation amount",
        native_unit_of_measurement="L",
    ),


    SonoffSWVSensorDescription(
        key="real_time_irrigation_volume",
        name="Real time irrigation volume",
        native_unit_of_measurement="L",
    ),


    SonoffSWVSensorDescription(
        key="real_time_irrigation_duration",
        name="Real time irrigation duration",
        native_unit_of_measurement="s",
    ),


    SonoffSWVSensorDescription(
        key="daily_irrigation_volume",
        name="Daily irrigation volume",
        native_unit_of_measurement="L",
    ),


    SonoffSWVSensorDescription(
        key="daily_irrigation_duration",
        name="Daily irrigation duration",
        native_unit_of_measurement="s",
    ),


    SonoffSWVSensorDescription(
        key="hour_irrigation_volume",
        name="Hour irrigation volume",
        native_unit_of_measurement="L",
    ),


    SonoffSWVSensorDescription(
        key="hour_irrigation_duration",
        name="Hour irrigation duration",
        native_unit_of_measurement="s",
    ),


    SonoffSWVSensorDescription(
        key="rain_delay",
        name="Rain delay",
    ),


    SonoffSWVSensorDescription(
        key="irrigation_schedule_status",
        name="Irrigation schedule status",
    ),

)



async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sonoff SWV sensors."""


    coordinator: SonoffSWVCoordinator = (
        hass.data[DOMAIN][entry.entry_id]
    )


    async_add_entities(

        SonoffSWVSensor(
            coordinator,
            description,
        )

        for description in SENSORS

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


        super().__init__(
            coordinator
        )


        self.entity_description = description


        self._attr_unique_id = (
            f"{coordinator.device_name}_"
            f"{description.key}"
        )



    @property
    def native_value(
        self,
    ):

        value = self.get_value()


        if isinstance(
            value,
            dict,
        ):

            return str(
                value
            )


        return value