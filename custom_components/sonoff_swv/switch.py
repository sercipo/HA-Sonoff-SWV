from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import (
    AddEntitiesCallback,
)

from .const import DOMAIN
from .descriptions import SwitchDescription
from .entity import SonoffSWVEntity


SWITCH_ENTITIES = (

    SwitchDescription(
        object_name="plan",
        key="enable_state",
        name="Plan enabled",
    ),

    SwitchDescription(
        object_name="weather",
        key="enable_rain_delay",
        name="Rain delay",
    ),

    SwitchDescription(
        object_name="weather",
        key="enable_humidity_delay",
        name="Humidity delay",
    ),

    SwitchDescription(
        object_name="weather",
        key="enable_frost_delay",
        name="Weather frost delay",
    ),

    SwitchDescription(
        object_name="alarm",
        key="enable_alarm_water_leak",
        name="Water leak alarm",
    ),

    SwitchDescription(
        object_name="alarm",
        key="enable_alarm_water_shortage",
        name="Water shortage alarm",
    ),

    SwitchDescription(
        object_name="alarm",
        key="enable_water_leak_auto_close",
        name="Leak auto close",
    ),

    SwitchDescription(
        object_name="alarm",
        key="enable_water_shortage_auto_close",
        name="Shortage auto close",
    ),

    SwitchDescription(
        object_name="alarm",
        key="enable_frost_protection",
        name="Frost protection",
    ),

)


async def async_setup_entry(

    hass: HomeAssistant,

    entry: ConfigEntry,

    async_add_entities: AddEntitiesCallback,

):

    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(

        SonoffSwitchEntity(

            coordinator,

            description,

        )

        for description in SWITCH_ENTITIES

    )


class SonoffSwitchEntity(

    SonoffSWVEntity,

    SwitchEntity,

):

    def __init__(

        self,

        coordinator,

        description,

    ):

        super().__init__(coordinator)

        self.description = description

        self._attr_unique_id = (

            f"{description.object_name}_{description.key}"

        )

        self._attr_name = description.name

    @property
    def is_on(self):

        obj = self.get_object()

        return getattr(

            obj,

            self.description.key,

        )

    async def async_turn_on(

        self,

        **kwargs,

    ):

        obj = self.get_object()

        setattr(

            obj,

            self.description.key,

            True,

        )

        await self._publish()

    async def async_turn_off(

        self,

        **kwargs,

    ):

        obj = self.get_object()

        setattr(

            obj,

            self.description.key,

            False,

        )

        await self._publish()

    async def _publish(

        self,

    ):

        if self.description.object_name == "plan":

            await self.coordinator.publish_plan()

        elif self.description.object_name == "manual":

            await self.coordinator.publish_manual()

        elif self.description.object_name == "weather":

            await self.coordinator.publish_weather()

        elif self.description.object_name == "seasonal":

            await self.coordinator.publish_seasonal()

        elif self.description.object_name == "alarm":

            await self.coordinator.publish_alarm()