from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.time import (
    TimeEntity,
    TimeEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import (
    AddEntitiesCallback,
)

from .const import DOMAIN
from .coordinator import SonoffSWVCoordinator
from .entity import SonoffSWVEntity
from datetime import time


@dataclass(frozen=True)
class SonoffSWVTimeDescription(
    TimeEntityDescription,
):
    """Description for Sonoff SWV time entities."""



TIMES = (

    SonoffSWVTimeDescription(
        key="irrigation_plan_start_time",
        name="Irrigation plan start time",
    ),

)



async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sonoff SWV time entities."""

    coordinator: SonoffSWVCoordinator = (
        hass.data[DOMAIN][entry.entry_id]
    )


    async_add_entities(

        SonoffSWVTime(
            coordinator,
            description,
        )

        for description in TIMES

    )



class SonoffSWVTime(
    SonoffSWVEntity,
    TimeEntity,
):
    """Sonoff SWV time entity."""

    entity_description: SonoffSWVTimeDescription



    def __init__(
        self,
        coordinator: SonoffSWVCoordinator,
        description: SonoffSWVTimeDescription,
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

        if value is None:
            return None

        if isinstance(value, time):
            return value

        try:

            parts = value.split(":")

            return time(
                hour=int(parts[0]),
                minute=int(parts[1]),
            )

        except (ValueError, AttributeError, IndexError):

            return None


    async def async_set_value(
        self,
        value,
    ) -> None:

        setattr(
            self.coordinator.device,
            self.entity_description.key,
            f"{value.hour:02d}:{value.minute:02d}",
        )


        await self.coordinator.publish_attribute(
            self.entity_description.key
        )


        self.async_write_ha_state()