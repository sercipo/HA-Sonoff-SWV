from __future__ import annotations

import json
import logging
from typing import Any

from homeassistant.components import mqtt
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)

from .mapper import build_payload_for_attribute
from .models.device import Device
from .mqtt import async_subscribe
from .storage import SonoffStorage
from .entity_resolver import find_mqtt_entity


_LOGGER = logging.getLogger(__name__)


HISTORY_PERIOD_24_HOURS = "24_hours"
HISTORY_PERIOD_30_DAYS = "30_days"
HISTORY_PERIOD_180_DAYS = "180_days"

HISTORY_PERIODS = (
    HISTORY_PERIOD_24_HOURS,
    HISTORY_PERIOD_30_DAYS,
    HISTORY_PERIOD_180_DAYS,
)

DEFAULT_HISTORY_PERIOD = HISTORY_PERIOD_24_HOURS


class SonoffSWVCoordinator(
    DataUpdateCoordinator[dict[str, Any]],
):
    """Coordinator for Sonoff SWV integration."""

    def __init__(
        self,
        hass: HomeAssistant,
        device_name: str,
        ieee: str | None = None,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="Sonoff SWV",
        )

        self.hass = hass

        self.storage = SonoffStorage(
            hass,
        )

        self.device_name = device_name

        # IEEE address coming from the config entry (resolved once, at
        # config_flow time, via the HA device_registry). This is the
        # authoritative source for device.ieee: it must NOT depend on
        # waiting for an MQTT state payload to arrive, since those are
        # not retained and may take a long time to show up after a
        # restart (e.g. battery-powered / event-driven devices).
        self._configured_ieee = ieee

        self.topic_state = f"zigbee2mqtt/{device_name}"

        self.topic_set = f"zigbee2mqtt/{device_name}/set"

        self.data: dict[str, Any] = {}

        self.device = Device()

        if self._configured_ieee:
            self.device.ieee = self._configured_ieee

        # Local integration setting.
        #
        # This is intentionally NOT part of Device
        # because the selected history period is not
        # a property of the Sonoff device.
        self.irrigation_history_period = DEFAULT_HISTORY_PERIOD

        _LOGGER.info(
            "Coordinator initialized for topic %s (ieee=%s)",
            self.topic_state,
            self.device.ieee or "unknown",
        )

    def get_mqtt_entity_id(
        self,
        mqtt_key: str,
    ) -> str | None:
        """Return the MQTT entity_id for a Zigbee2MQTT property."""

        if not self.device.ieee:
            return None

        return find_mqtt_entity(
            self.hass,
            self.device.ieee,
            mqtt_key,
        )

    async def async_initialize(
        self,
    ) -> None:
        """Load stored data."""

        self.data = await self.storage.load()

        stored_device = self.data.get(
            "device",
            {},
        )

        if stored_device:
            self.device = Device.from_storage_dict(
                stored_device,
            )

        # The config entry's IEEE is always authoritative, even after
        # restoring a previously stored Device snapshot: it is resolved
        # from the HA device_registry at config_flow time and does not
        # depend on MQTT payload timing. This also self-heals any old
        # storage snapshot saved before this mechanism existed (empty
        # or stale ieee).
        if self._configured_ieee:
            self.device.ieee = self._configured_ieee

        self.irrigation_history_period = self.data.get(
            "irrigation_history_period",
            DEFAULT_HISTORY_PERIOD,
        )

        if self.irrigation_history_period not in HISTORY_PERIODS:
            self.irrigation_history_period = DEFAULT_HISTORY_PERIOD

        self.async_set_updated_data(
            self.data,
        )

    async def async_set_history_period(
        self,
        period: str,
    ) -> None:
        """Set and persist the selected history period."""

        if period not in HISTORY_PERIODS:
            _LOGGER.warning(
                "Invalid irrigation history period: %s",
                period,
            )
            return

        self.irrigation_history_period = period

        self.data["irrigation_history_period"] = period

        await self.async_save()

        self.async_set_updated_data(
            self.data,
        )

        _LOGGER.debug(
            "Irrigation history period set to %s",
            period,
        )

    def update_from_device(
        self,
        payload: dict[str, Any],
    ) -> None:
        """Update Device from Zigbee2MQTT payload."""

        _LOGGER.debug(
            "Coordinator update: %s",
            payload,
        )

        self._update_device_from_payload(
            payload,
        )

        _LOGGER.debug(
            "Device model updated: %s",
            self.device,
        )

        self.data["device"] = self.device.to_storage_dict()

        self.async_set_updated_data(
            self.data,
        )

        self.hass.async_create_task(
            self.async_save(),
        )

    def _update_device_from_payload(
        self,
        payload: dict[str, Any],
    ) -> None:
        """Normalize Zigbee2MQTT payload into flat Device model."""

        self.device.update_from_z2m_payload(
            payload,
        )

        # The MQTT payload's own "device.ieeeAddr" field (when present)
        # is a secondary confirmation, but the config-entry-resolved
        # IEEE remains authoritative -- it must never be overwritten by
        # a payload, since that would reintroduce the "wait for MQTT to
        # find out who I am" fragility this was meant to remove.
        if self._configured_ieee:
            self.device.ieee = self._configured_ieee

    async def publish_attribute(
        self,
        attribute: str,
    ) -> None:
        """Publish changed Device attribute."""

        payload = build_payload_for_attribute(
            self.device,
            attribute,
        )

        if not payload:
            return

        await mqtt.async_publish(
            self.hass,
            self.topic_set,
            json.dumps(payload),
            qos=0,
            retain=False,
        )

        self.data["device"] = self.device.to_storage_dict()

        await self.async_save()

        self.async_set_updated_data(
            self.data,
        )

    async def publish_command(
        self,
        command: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        """Publish MQTT command."""

        mqtt_payload = {
            command: payload or {},
        }

        _LOGGER.debug(
            "Publishing MQTT command %s: %s",
            command,
            mqtt_payload,
        )

        await mqtt.async_publish(
            self.hass,
            self.topic_set,
            json.dumps(mqtt_payload),
            qos=0,
            retain=False,
        )

    async def async_save(
        self,
    ) -> None:
        """Save local storage."""

        await self.storage.save(
            self.data,
        )

    async def async_start(
        self,
    ) -> None:
        """Start MQTT listener."""

        _LOGGER.info(
            "Starting MQTT subscription: %s",
            self.topic_state,
        )

        self._unsubscribe = await async_subscribe(
            self.hass,
            self,
        )

    async def async_stop(
        self,
    ) -> None:
        """Stop MQTT listener."""

        if hasattr(
            self,
            "_unsubscribe",
        ):
            self._unsubscribe()
