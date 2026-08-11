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
from .coordinator import (
    DEFAULT_HISTORY_PERIOD,
    HISTORY_PERIODS,
    SonoffSWVCoordinator,
)
from .entity import SonoffSWVEntity


@dataclass(frozen=True)
class SonoffSWVSelectDescription(
    SelectEntityDescription,
):
    """Description for Sonoff SWV select entities."""

    options: tuple[str, ...] = ()


HISTORY_PERIOD_OPTIONS = {
    "24_hours": "24 hours",
    "30_days": "30 days",
    "180_days": "180 days",
}


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
            "odd_days",
            "even_days",
            "day_interval",
            "weekdays",
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
    SonoffSWVSelectDescription(
        key="irrigation_history_period",
        name="Irrigation history period",
        icon="mdi:calendar-range",
        options=(
            "24 hours",
            "30 days",
            "180 days",
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sonoff SWV select entities."""

    coordinator: SonoffSWVCoordinator = hass.data[DOMAIN][entry.entry_id]

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
            coordinator,
        )

        self.entity_description = description

        self._attr_unique_id = f"{coordinator.device_name}_" f"{description.key}"

        self._attr_options = list(description.options)

        if description.key == "irrigation_history_period":
            current_period = coordinator.irrigation_history_period

            if current_period not in HISTORY_PERIOD_OPTIONS:
                current_period = DEFAULT_HISTORY_PERIOD

            self._attr_current_option = HISTORY_PERIOD_OPTIONS[current_period]

    @property
    def current_option(
        self,
    ) -> str | None:
        """Return the currently selected option."""

        if self.entity_description.key == "irrigation_history_period":
            return self._attr_current_option

        value = self.get_value()

        if value in self.options:
            return value

        return None

    async def async_select_option(
        self,
        option: str,
    ) -> None:
        """Handle select option."""

        if self.entity_description.key == "irrigation_history_period":
            period = next(
                (
                    key
                    for key, label in HISTORY_PERIOD_OPTIONS.items()
                    if label == option
                ),
                None,
            )

            if period is None:
                return

            await self.coordinator.async_set_history_period(
                period,
            )

            self._attr_current_option = option

            self.async_write_ha_state()
            return

        if option not in self.options:
            return

        setattr(
            self.coordinator.device,
            self.entity_description.key,
            option,
        )

        await self.coordinator.publish_attribute(
            self.entity_description.key,
        )

        self.async_write_ha_state()
