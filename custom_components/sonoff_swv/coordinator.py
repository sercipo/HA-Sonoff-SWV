from __future__ import annotations

import json
import logging
import asyncio
from typing import Any

from homeassistant.components import mqtt
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)

from .mapper import build_payload_for_attribute, build_payload_for_group, get_mapping
from .models.device import Device
from .mqtt import async_subscribe
from .irrigation_history import (
    build_event_from_status,
    prune_history,
    upsert_event,
)
from datetime import datetime
from .irrigation_plans import (
    form_values_from_plan,
    normalize_plan,
    plan_from_form,
    remove_plan,
    upsert_plan,
    PLAN_DEFAULTS,
)
from .storage import SonoffStorage
from .entity_resolver import find_mqtt_entity

# Gruppi di impostazioni trattati come bozza: scrivono sul device
# solo quando un bottone chiama publish_attribute(..., force=True).
DRAFT_GROUPS = ("irrigation_plan_settings", "manual_default_settings")

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

HISTORY_PERIOD_MQTT_TYPE = {
    HISTORY_PERIOD_24_HOURS: "24_hours",
    HISTORY_PERIOD_30_DAYS: "30_days",
    HISTORY_PERIOD_180_DAYS: "6_months",
}


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

        if "irrigation_schedule_status" in payload:

            event = build_event_from_status(
                self.device.irrigation_schedule_status,
            )

            if event is not None:

                history = self.data.get(
                    "irrigation_history",
                    [],
                )

                history = upsert_event(
                    history,
                    event,
                )

                self.data["irrigation_history"] = prune_history(
                    history,
                )

        report = payload.get("irrigation_plan_report")

        if isinstance(report, dict) and report != self.data.get("last_plan_report"):

            plan = normalize_plan(
                report,
                "report",
                datetime.now().astimezone(),
            )

            if plan is not None:
                self.data["irrigation_plans"] = upsert_plan(
                    self.data.get("irrigation_plans", {}),
                    plan,
                )

            self.data["last_plan_report"] = report

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
        force: bool = False,
    ) -> None:
        """Publish changed Device attribute.

        Attributes belonging to a composite group (irrigation_plan_settings,
        manual_default_settings, valve_alarm_settings)
        are published as the full group payload, not the single field: the
        zigbee-herdsman-converters SWV-ZFE converter (>=26.90.0) requires
        atomic writes for these composites and silently mishandles partial
        payloads. Direct attributes (no group) are unaffected.
        """

        mapping = get_mapping(
            attribute,
        )

        # I campi del piano sono una bozza: non scrivono sul device finché
        # non viene premuto il bottone di salvataggio (force=True).
        if (
            mapping is not None
            and mapping.group in DRAFT_GROUPS
            and not force
        ):
            _LOGGER.debug(
                "Draft field %s changed: not published",
                attribute,
            )
            return

        if mapping is not None and mapping.group is not None:

            payload = build_payload_for_group(
                self.device,
                mapping.group,
            )

        else:

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

    async def async_archive_plan_from_form(self) -> None:
        """Archivia il piano attualmente nel form (dopo un salvataggio da HA)."""
        raw = plan_from_form(
            lambda attr: getattr(self.device, attr, None),
            self.device.irrigation_plan_index,
        )
        plan = normalize_plan(raw, "ha_write", datetime.now().astimezone())

        if plan is None:
            return

        self.data["irrigation_plans"] = upsert_plan(
            self.data.get("irrigation_plans", {}),
            plan,
        )
        self.async_set_updated_data(self.data)
        await self.async_save()

    async def async_load_plan_into_form(self, plan_index: int) -> None:
        """Popola il form con il piano archiviato, o con i default se non noto."""
        plan = self.data.get("irrigation_plans", {}).get(str(plan_index))

        if plan is None:
            plan = PLAN_DEFAULTS

        for attr, value in form_values_from_plan(plan).items():
            setattr(self.device, attr, value)

        self.data["device"] = self.device.to_storage_dict()
        self.async_set_updated_data(self.data)
        await self.async_save()

    async def async_forget_plan(self, plan_index: int) -> None:
        """Rimuove il piano dall'archivio (dopo un remove sul device)."""

        # Il device non azzera lo status dopo una rimozione: ricordo l'impronta
        # di quello status così da non segnalarlo come disallineamento.
        status = self.device.irrigation_schedule_status
        if isinstance(status, dict) and status.get("schedule_index") == plan_index:
            self.data["status_ignored"] = {
                "schedule_index": status.get("schedule_index"),
                "start_time": status.get("start_time"),
            }

        self.data["irrigation_plans"] = remove_plan(
            self.data.get("irrigation_plans", {}),
            plan_index,
        )

        await self.async_load_plan_into_form(plan_index)

    async def async_remove_all_plans(
        self,
        command: str,
        indexes=range(6),
    ) -> None:
        """Rimuove tutti i piani dal device e svuota l'archivio."""

        for i in indexes:
            await self.publish_command(command, {"plan_index": i})
            await asyncio.sleep(2)

        # Il device non azzera lo status dopo le rimozioni: ne ricordo
        # l'impronta per non segnalarlo come disallineamento.
        status = self.device.irrigation_schedule_status
        if isinstance(status, dict) and status.get("schedule_status") == "standby":
            self.data["status_ignored"] = {
                "schedule_index": status.get("schedule_index"),
                "start_time": status.get("start_time"),
            }

        self.data["irrigation_plans"] = {}

        await self.async_load_plan_into_form(self.device.irrigation_plan_index)

    async def _publish_valve(self, on: bool) -> None:
        await mqtt.async_publish(
            self.hass,
            self.topic_set,
            json.dumps({"state": "ON" if on else "OFF"}),
            qos=0,
            retain=False,
        )

    async def async_start_manual_irrigation(self) -> None:
        """Invia le impostazioni manuali e poi apre la valvola."""

        # Se è già aperta non si tocca niente: non si riavvia un'irrigazione in corso.
        if self.device.state == "ON":
            _LOGGER.warning("Valvola già aperta: avvio manuale ignorato")
            return

        await self.publish_attribute("manual_irrigation_mode", force=True)
        await asyncio.sleep(2)
        await self._publish_valve(True)

    async def async_stop_irrigation(self) -> None:
        """Chiude la valvola."""
        await self._publish_valve(False)

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
