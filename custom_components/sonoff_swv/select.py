from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.select import (
    SelectEntity,
    SelectEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import (
    AddEntitiesCallback,
)

from .const import DOMAIN
from .coordinator import SonoffSWVCoordinator
from .entity import SonoffSWVEntity


@dataclass(frozen=True)
class SonoffSWVSelectDescription(
    SelectEntityDescription,
):
    """Description for Sonoff SWV selects."""

    options: tuple[str, ...] = ()



SELECTS = (

    SonoffSWVSelectDescription(
        key="irrigation_plan_mode",
        name="Irrigation plan mode",
        options=(
            "duration",
            "capacity",
        ),
    ),


        SonoffSWVSelectDescription(
        key="irrigation_plan_loop_type",
        name="Irrigation plan loop type",
        options=(
            "day_interval",
            "week_days",
        ),
    ),


    SonoffSWVSelectDescription(
        key="manual_irrigation_mode",
        name="Manual irrigation mode",
        options=(
            "duration",
            "capacity",
        ),
    ),

)



async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sonoff SWV select entities."""

    coordinator: SonoffSWVCoordinator = (
        hass.data[DOMAIN][entry.entry_id]
    )


    async_add_entities(

        SonoffSWVSelect(
            coordinator,
            description,
        )

        for description in SELECTS

    )



class SonoffSWVSelect(
    SonoffSWVEntity,
    SelectEntity,
):
    """Sonoff SWV select entity."""

    entity_description: SonoffSWVSelectDescription



    def __init__(
        self,
        coordinator: SonoffSWVCoordinator,
        description: SonoffSWVSelectDescription,
    ) -> None:

        super().__init__(
            coordinator
        )


        self.entity_description = description


        self._attr_unique_id = (
            f"{coordinator.device_name}_"
            f"{description.key}"
        )


        self._attr_options = list(
            description.options
        )



    @property
    def current_option(
        self,
    ) -> str | None:

        value = self.get_value()

        if value in self.options:
            return value

        return None



    async def async_select_option(
        self,
        option: str,
    ) -> None:

        setattr(
            self.coordinator.device,
            self.entity_description.key,
            option,
        )


        await self.coordinator.publish_attribute(
            self.entity_description.key
        )


        self.async_write_ha_state()