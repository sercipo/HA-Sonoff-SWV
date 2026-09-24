from __future__ import annotations

from datetime import date, datetime
from dataclasses import dataclass

from homeassistant.components.date import (
    DateEntity,
    DateEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import (
    AddEntitiesCallback,
)

from .const import DOMAIN
from .coordinator import SonoffSWVCoordinator
from .entity import SonoffSWVEntity
from .entity_resolver import find_mqtt_entity
from .entity_setup import async_add_entities_after_start


@dataclass(frozen=True)
class SonoffSWVDateDescription(
    DateEntityDescription,
):
    """Description for Sonoff SWV date entities."""


DATES = (

    SonoffSWVDateDescription(
        key="irrigation_plan_enable_date",
        name="Irrigation plan enable date",
    ),

)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sonoff SWV date entities."""

    coordinator: SonoffSWVCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities_after_start(
        hass,
        async_add_entities,
        coordinator,
        DATES,
        SonoffSWVDate,
        "date",
    )


class SonoffSWVDate(
    SonoffSWVEntity,
    DateEntity,
):
    """Sonoff SWV date entity."""

    entity_description: SonoffSWVDateDescription

    def __init__(
        self,
        coordinator: SonoffSWVCoordinator,
        description: SonoffSWVDateDescription,
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

        if isinstance(value, date):
            return value

        try:

            return date.fromisoformat(value)

        except (ValueError, AttributeError):

            return None

    async def async_set_value(
        self,
        value: date,
    ) -> None:

        setattr(
            self.coordinator.device,
            self.entity_description.key,
            value.isoformat(),
        )

        await self.coordinator.publish_attribute(
            self.entity_description.key
        )

        self.async_write_ha_state()