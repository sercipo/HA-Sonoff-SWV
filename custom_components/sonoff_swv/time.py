from __future__ import annotations

from datetime import time

from homeassistant.components.time import TimeEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .entity import SonoffSWVEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):

    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            PlanStartTimeEntity(
                coordinator,
            )
        ]
    )


class PlanStartTimeEntity(
    SonoffSWVEntity,
    TimeEntity,
):

    _attr_has_entity_name = True

    _attr_name = "Plan 0 start time"

    def __init__(
        self,
        coordinator,
    ):

        super().__init__(coordinator)

        self._attr_unique_id = (
            "plan0_start_time"
        )

    @property
    def native_value(self):

        text = self.coordinator.plan.start_time

        hour, minute = map(
            int,
            text.split(":"),
        )

        return time(
            hour,
            minute,
        )

    async def async_set_value(
        self,
        value: time,
    ):

        self.coordinator.plan.start_time = (
            value.strftime("%H:%M")
        )

        await self.coordinator.publish_plan()
