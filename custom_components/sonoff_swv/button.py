from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.button import (
    ButtonEntity,
    ButtonEntityDescription,
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
class SonoffSWVButtonDescription(
    ButtonEntityDescription,
):
    """Description for Sonoff SWV buttons."""

    command: str = ""


BUTTONS = (

    SonoffSWVButtonDescription(
        key="read_irrigation_history",
        name="Read irrigation history",
        command="read_irrigation_history",
    ),

    SonoffSWVButtonDescription(
        key="irrigation_plan_report",
        name="Irrigation plan report",
        command="irrigation_plan_report",
    ),

    SonoffSWVButtonDescription(
        key="irrigation_plan_remove",
        name="Irrigation plan remove",
        command="irrigation_plan_remove",
    ),

    SonoffSWVButtonDescription(
        key="irrigation_plan_settings",
        name="Irrigation plan settings",
        command="irrigation_plan_settings",
    ),

)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sonoff SWV buttons."""

    coordinator: SonoffSWVCoordinator = (
        hass.data[DOMAIN][entry.entry_id]
    )

    async_add_entities(
        SonoffSWVButton(
            coordinator,
            description,
        )
        for description in BUTTONS
    )


class SonoffSWVButton(
    SonoffSWVEntity,
    ButtonEntity,
):
    """Sonoff SWV button entity."""

    entity_description: SonoffSWVButtonDescription


    def __init__(
        self,
        coordinator: SonoffSWVCoordinator,
        description: SonoffSWVButtonDescription,
    ) -> None:

        super().__init__(
            coordinator
        )

        self.entity_description = description

        self._attr_unique_id = (
            f"{coordinator.device_name}_"
            f"{description.key}"
        )


    async def async_press(
        self,
    ) -> None:
        """Execute MQTT command."""

        await self.coordinator.publish_command(
            self.entity_description.command
        )