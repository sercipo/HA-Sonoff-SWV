from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


class SonoffSWVEntity(CoordinatorEntity):

    def __init__(
        self,
        coordinator,
    ):

        super().__init__(coordinator)

        self._attr_has_entity_name = True

    @property
    def device_info(self):

        device = self.coordinator.device

        if device is None:

            return None

        return DeviceInfo(

            identifiers={
                (
                    DOMAIN,
                    device.ieee,
                )
            },

            manufacturer="SONOFF",

            model=device.model,

            name=self.coordinator.device_name,

            sw_version=device.firmware,

        )

    def get_object(self):

        return getattr(

            self.coordinator.device,

            self.description.object_name,

        )