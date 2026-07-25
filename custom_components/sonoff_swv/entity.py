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
                    device.ieeeAddr,
                )
            },

            manufacturer=device.manufacturerName,

            model=device.model,

            name=device.friendlyName,

            sw_version=device.softwareBuildID,

            hw_version=str(
                device.hardwareVersion
            ),

        )

    def get_object(self):

        return self.coordinator.get_object(

            self.description.object_name

        )