from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .descriptions import NumberDescription
from .entity import SonoffSWVEntity


NUMBER_ENTITIES = (

    NumberDescription(
        object_name="plan",
        key="irrigation_amount",
        name="Irrigation amount",
        min_value=1,
        max_value=99,
        step=1,
        unit=UnitOfVolume.LITERS,
    ),

    NumberDescription(
        object_name="plan",
        key="loop_type_interval_days",
        name="Interval days",
        min_value=1,
        max_value=30,
        step=1,
    ),

    NumberDescription(
        object_name="plan",
        key="fail_safe",
        name="Fail safe",
        min_value=1,
        max_value=30,
        step=1,
    ),

    NumberDescription(
        object_name="manual",
        key="irrigation_amount",
        name="Manual irrigation amount",
        min_value=1,
        max_value=99,
        step=1,
        unit=UnitOfVolume.LITERS,
    ),

    NumberDescription(
        object_name="manual",
        key="fail_safe",
        name="Manual fail safe",
        min_value=1,
        max_value=30,
        step=1,
    ),

)


async def async_setup_entry(

    hass: HomeAssistant,

    entry: ConfigEntry,

    async_add_entities: AddEntitiesCallback,

):

    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(

        SonoffNumberEntity(

            coordinator,

            description,

        )

        for description in NUMBER_ENTITIES

    )


class SonoffNumberEntity(

    SonoffSWVEntity,

    NumberEntity,

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

        self._attr_native_min_value = (

            description.min_value

        )

        self._attr_native_max_value = (

            description.max_value

        )

        self._attr_native_step = (

            description.step

        )

        self._attr_native_unit_of_measurement = (

            description.unit

        )

    @property
    def native_value(self):

        obj = self.get_object()

        return getattr(

            obj,

            self.description.key,

        )

    async def async_set_native_value(

        self,

        value,

    ):

        obj = self.get_object()

        setattr(

            obj,

            self.description.key,

            int(value),

        )

        if self.description.object_name == "plan":

            await self.coordinator.publish_plan()

        elif self.description.object_name == "manual":

            await self.coordinator.publish_manual()