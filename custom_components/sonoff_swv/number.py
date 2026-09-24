from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.core import callback
from homeassistant.helpers.event import async_track_state_change_event
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

WATER_FLOW_UNIT_MAP = {
    "liter": "L",
    "us_gallon": "gal",
    "imperial_gallon": "gal (UK)",
}

AMOUNT_UNIT_KEYS = (
    "manual_irrigation_amount",
    "irrigation_plan_amount",
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

    async def async_added_to_hass(
        self,
    ) -> None:

        await super().async_added_to_hass()

        if self.entity_description.key not in AMOUNT_UNIT_KEYS:
            return

        entity_id = self.get_mqtt_entity_id(
            "water_flow_unit",
        )

        if not entity_id:
            return

        @callback
        def _water_flow_unit_changed(
            _event,
        ) -> None:

            self.async_write_ha_state()

        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                [entity_id],
                _water_flow_unit_changed,
            )
        )

    @property
    def native_unit_of_measurement(
        self,
    ) -> str | None:

        if self.entity_description.key not in AMOUNT_UNIT_KEYS:
            return self.entity_description.native_unit_of_measurement

        entity_id = self.get_mqtt_entity_id(
            "water_flow_unit",
        )

        if entity_id:

            state = self.hass.states.get(entity_id)

            if state and state.state in WATER_FLOW_UNIT_MAP:
                return WATER_FLOW_UNIT_MAP[state.state]

        return self.entity_description.native_unit_of_measurement

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