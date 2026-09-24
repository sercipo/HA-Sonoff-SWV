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
from .entity_resolver import find_mqtt_entity
from .entity_setup import async_add_entities_after_start


@dataclass(frozen=True)
class SonoffSWVNumberDescription(
    NumberEntityDescription,
):
    """Description for Sonoff SWV number entities."""


NUMBERS = (
    SonoffSWVNumberDescription(
        key="irrigation_plan_index",
        name="Irrigation plan index",
        native_min_value=0,
        native_max_value=5,
        native_step=1,
    ),
    SonoffSWVNumberDescription(
        key="manual_irrigation_amount",
        name="Manual irrigation amount",
        native_min_value=0,
        native_max_value=10000,
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
        native_max_value=10000,
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
        native_min_value=1,
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

    coordinator: SonoffSWVCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities_after_start(
        hass,
        async_add_entities,
        coordinator,
        NUMBERS,
        SonoffSWVNumber,
        "number",
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

        super().__init__(coordinator)

        self.entity_description = description


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

        key = self.entity_description.key

        setattr(
            self.coordinator.device,
            key,
            int(value),
        )

        # irrigation_plan_index is a passive selector: it only marks
        # which plan slot (0-5) subsequent operations should target.
        # It does not trigger any MQTT write on its own -- that is
        # done by the "Irrigation plan settings" / "Irrigation plan
        # remove" buttons, which read this value when pressed.
        if key != "irrigation_plan_index":

            await self.coordinator.publish_attribute(key)

        self.async_write_ha_state()