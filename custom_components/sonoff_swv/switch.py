from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.switch import (
    SwitchEntity,
    SwitchEntityDescription,
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
class SonoffSWVSwitchDescription(
    SwitchEntityDescription,
):
    """Description for Sonoff SWV switches."""


SWITCHES = (

    SonoffSWVSwitchDescription(
        key="state",
        name="Valve",
    ),

    SonoffSWVSwitchDescription(
        key="child_lock",
        name="Child lock",
    ),

    SonoffSWVSwitchDescription(
        key="irrigation_plan_enabled",
        name="Irrigation plan enabled",
    ),

    SonoffSWVSwitchDescription(
        key="enable_alarm_water_shortage",
        name="Water shortage alarm",
    ),

    SonoffSWVSwitchDescription(
        key="enable_alarm_water_leak",
        name="Water leak alarm",
    ),

    SonoffSWVSwitchDescription(
        key="enable_water_shortage_auto_close",
        name="Water shortage auto close",
    ),

    SonoffSWVSwitchDescription(
        key="enable_water_leak_auto_close",
        name="Water leak auto close",
    ),

    #SonoffSWVSwitchDescription(
    #    key="enable_frost_protection",
    #    name="Frost protection",
    #),

)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sonoff SWV switches."""

    coordinator: SonoffSWVCoordinator = (
        hass.data[DOMAIN][entry.entry_id]
    )

    async_add_entities(
        SonoffSWVSwitch(
            coordinator,
            description,
        )
        for description in SWITCHES
    )


class SonoffSWVSwitch(
    SonoffSWVEntity,
    SwitchEntity,
):
    """Sonoff SWV switch entity."""

    entity_description: SonoffSWVSwitchDescription


    def __init__(
        self,
        coordinator: SonoffSWVCoordinator,
        description: SonoffSWVSwitchDescription,
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
    def is_on(
        self,
    ) -> bool:
        """Return switch state."""

        value = self.get_value()

        if isinstance(
            value,
            str,
        ):

            return value.upper() in (
                "ON",
                "LOCK",
                "TRUE",
            )

        return bool(value)



    async def async_turn_on(
        self,
        **kwargs,
    ) -> None:
        """Turn switch on."""

        key = self.entity_description.key


        if key == "child_lock":

            value = "LOCK"

        elif key == "state":

            value = "ON"

        else:

            value = True


        setattr(
            self.coordinator.device,
            key,
            value,
        )


        await self.coordinator.publish_attribute(
            key
        )


        self.async_write_ha_state()



    async def async_turn_off(
        self,
        **kwargs,
    ) -> None:
        """Turn switch off."""

        key = self.entity_description.key


        if key == "child_lock":

            value = "UNLOCK"

        elif key == "state":

            value = "OFF"

        else:

            value = False


        setattr(
            self.coordinator.device,
            key,
            value,
        )


        await self.coordinator.publish_attribute(
            key
        )


        self.async_write_ha_state()