"""Entità text locali di Sonoff SWV (nessuna scrittura sul device)."""
from __future__ import annotations

from homeassistant.components.text import (
    TextEntity,
    TextEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import (
    AddEntitiesCallback,
)

from .const import DOMAIN
from .coordinator import SonoffSWVCoordinator
from .entity import SonoffSWVEntity
from .entity_setup import async_add_entities_after_start

TEXTS = (
    TextEntityDescription(
        key="notify_device_label",
        name="Notify device label",
    ),
)


class SonoffSWVNotifyText(
    SonoffSWVEntity,
    TextEntity,
):
    """Nome del device usato nei messaggi di notifica."""

    entity_description: TextEntityDescription

    _attr_native_min = 0
    _attr_native_max = 40

    def __init__(
        self,
        coordinator: SonoffSWVCoordinator,
        description: TextEntityDescription,
    ) -> None:
        super().__init__(coordinator)

        self.entity_description = description

        self._attr_unique_id = f"{coordinator.device_name}_{description.key}"

    @property
    def available(self) -> bool:
        return super().available and bool(
            self.coordinator.notify_setting("target")
        )

    @property
    def native_value(self) -> str:
        return self.coordinator.notify_label()

    async def async_set_value(self, value: str) -> None:
        # Un campo vuoto riporta al nome di Z2M.
        await self.coordinator.async_set_notify_setting(
            "device_label",
            value.strip() or None,
        )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sonoff SWV text entities."""

    coordinator: SonoffSWVCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities_after_start(
        hass,
        async_add_entities,
        coordinator,
        TEXTS,
        SonoffSWVNotifyText,
        "text",
    )