from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import DOMAIN
from .coordinator import SonoffSWVCoordinator
from .entity_resolver import find_mqtt_entity


class SonoffSWVEntity(
    CoordinatorEntity[SonoffSWVCoordinator],
):
    """Base entity for Sonoff SWV."""

    def __init__(
        self,
        coordinator: SonoffSWVCoordinator,
    ) -> None:

        super().__init__(coordinator)

        self._attr_has_entity_name = True

    def get_mqtt_entity_id(
        self,
        mqtt_key: str,
    ) -> str | None:
        """Return the MQTT entity_id for a stable MQTT key."""

        device = self.coordinator.device

        if not device.ieee:
            return None

        return find_mqtt_entity(
            self.hass,
            device.ieee,
            mqtt_key,
        )  

    def mqtt_entity_exists(
        self,
        mqtt_key: str,
    ) -> bool:
        """Return True if an MQTT entity exists for the MQTT key."""

        return self.get_mqtt_entity_id(mqtt_key) is not None

    @property
    def device_info(
        self,
    ) -> DeviceInfo | None:
        """Return device registry information."""

        device = self.coordinator.device

        if not device.ieee:

            return None

        return DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    device.ieee,
                )
            },
            manufacturer=(device.manufacturer or "SONOFF"),
            model=device.model or None,
            name=(device.friendly_name or self.coordinator.device_name),
            sw_version=device.firmware or None,
            hw_version=device.hardware or None,
        )

    @property
    def unique_id(
        self,
    ) -> str | None:
        """Return unique entity id."""

        if not self.entity_description:
            return None

        return f"{self.coordinator.device.ieee}_" f"{self.entity_description.key}"

    def get_value(
        self,
    ) -> Any:
        """Return value from Device model."""

        if not self.entity_description:

            return None

        return getattr(
            self.coordinator.device,
            self.entity_description.key,
            None,
        )
