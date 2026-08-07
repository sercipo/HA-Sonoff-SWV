from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
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
class SonoffSWVNumberDescription(
    NumberEntityDescription,
):
    """Description for Sonoff SWV number entities."""


NUMBERS = (

    SonoffSWVNumberDescription(
        key="manual_irrigation_amount",
        name="Manual irrigation amount",
        native_min_value=0,
        native_max_value=999,
        native_step=1,
        native_unit_of_measurement="L",
    ),

    SonoffSWVNumberDescription(
        key="manual_irrigation_duration",
        name="Manual irrigation duration",
        native_min_value=1,
        native_max_value=719,
        native_step=1,
        native_unit_of_measurement="min",
    ),

    SonoffSWVNumberDescription(
        key="manual_irrigation_total_duration",
        name="Manual irrigation total duration",
        native_min_value=1,
        native_max_value=719,
        native_step=1,
        native_unit_of_measurement="min",
    ),

    SonoffSWVNumberDescription(
        key="manual_interval_duration",
        name="Manual interval duration",
        native_min_value=0,
        native_max_value=719,
        native_step=1,
        native_unit_of_measurement="min",
    ),

    SonoffSWVNumberDescription(
        key="manual_fail_safe",
        name="Manual fail safe",
        native_min_value=0,
        native_max_value=719,
        native_step=1,
        native_unit_of_measurement="min",
    ),


    SonoffSWVNumberDescription(
        key="irrigation_plan_amount",
        name="Irrigation plan amount",
        native_min_value=0,
        native_max_value=999,
        native_step=1,
        native_unit_of_measurement="L",
    ),

    SonoffSWVNumberDescription(
        key="irrigation_plan_duration",
        name="Irrigation plan duration",
        native_min_value=1,
        native_max_value=60,
        native_step=1,
        native_unit_of_measurement="min",
    ),

    SonoffSWVNumberDescription(
        key="irrigation_plan_total_duration",
        name="Irrigation plan total duration",
        native_min_value=0,
        native_max_value=719,
        native_step=1,
        native_unit_of_measurement="min",
    ),

    SonoffSWVNumberDescription(
        key="irrigation_plan_interval_duration",
        name="Irrigation plan interval duration",
        native_min_value=0,
        native_max_value=60,
        native_step=1,
        native_unit_of_measurement="min",
    ),

    SonoffSWVNumberDescription(
        key="irrigation_plan_interval_days",
        name="Irrigation plan interval days",
        native_min_value=0,
        native_max_value=30,
        native_step=1,
        native_unit_of_measurement="days",
    ),

    SonoffSWVNumberDescription(
        key="irrigation_plan_fail_safe",
        name="Irrigation plan fail safe",
        native_min_value=0,
        native_max_value=719,
        native_step=1,
        native_unit_of_measurement="min",
    ),

)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sonoff SWV number entities."""

    coordinator: SonoffSWVCoordinator = (
        hass.data[DOMAIN][entry.entry_id]
    )

    async_add_entities(
        SonoffSWVNumber(
            coordinator,
            description,
        )
        for description in NUMBERS
    )


class SonoffSWVNumber(
    SonoffSWVEntity,
    NumberEntity,
):
    """Sonoff SWV number entity."""

    entity_description: SonoffSWVNumberDescription


    def __init__(
        self,
        coordinator: SonoffSWVCoordinator,
        description: SonoffSWVNumberDescription,
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
    ) -> int | float | None:

        value = self.get_value()

        if value is None:
            return None

        return int(value)


    async def async_set_native_value(
        self,
        value: float,
    ) -> None:

        setattr(
            self.coordinator.device,
            self.entity_description.key,
            int(value),
        )

        await self.coordinator.publish_attribute(
            self.entity_description.key
        )

        self.async_write_ha_state()