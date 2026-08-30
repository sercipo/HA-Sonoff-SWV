from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import selector

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

CONF_DEVICE_ID = "device_id"

# Domain used by Home Assistant's MQTT integration when registering
# devices discovered via Zigbee2MQTT.
#
# Verified against a live core.device_registry dump: the identifier
# tuple is ("mqtt", "zigbee2mqtt_<ieee>"), NOT ("zigbee2mqtt", "<ieee>").
# Do not "fix" this without re-checking a real registry entry.
MQTT_DEVICE_REGISTRY_DOMAIN = "mqtt"

# Prefix Zigbee2MQTT uses inside the second identifier element, e.g.
# ("mqtt", "zigbee2mqtt_0xa4c138140df0ffff").
ZIGBEE2MQTT_IDENTIFIER_PREFIX = "zigbee2mqtt_"


def _extract_ieee(device_entry: dr.DeviceEntry) -> str | None:
    """Extract the stable IEEE address from a device_registry entry's
    identifiers, if it looks like a Zigbee2MQTT device.

    Returns None if the selected device was not registered by
    Zigbee2MQTT via the MQTT integration (e.g. the user picked an
    unrelated MQTT device).
    """
    for domain, identifier in device_entry.identifiers:
        if domain != MQTT_DEVICE_REGISTRY_DOMAIN:
            continue
        if not identifier.startswith(ZIGBEE2MQTT_IDENTIFIER_PREFIX):
            continue
        return identifier[len(ZIGBEE2MQTT_IDENTIFIER_PREFIX):]
    return None


class SonoffSWVConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:

        errors: dict[str, str] = {}

        if user_input is not None:
            device_registry = dr.async_get(self.hass)
            device_entry = device_registry.async_get(
                user_input[CONF_DEVICE_ID]
            )

            if device_entry is None:
                errors["base"] = "device_not_found"
            else:
                ieee = _extract_ieee(device_entry)

                if ieee is None:
                    errors["base"] = "not_a_zigbee2mqtt_device"
                else:
                    # Use the registry's own `name` (populated from the
                    # Zigbee2MQTT discovery payload), NOT `name_by_user`.
                    # `name_by_user` is only a display override the user
                    # may have set in HA; the actual MQTT topics
                    # ("zigbee2mqtt/<friendly_name>/...") always follow
                    # the Zigbee2MQTT-side friendly_name, which is what
                    # `name` reflects here.
                    device_name = device_entry.name

                    # Prevent configuring the same physical valve twice.
                    await self.async_set_unique_id(ieee)
                    self._abort_if_unique_id_configured()

                    _LOGGER.info(
                        "Configuring Sonoff SWV for device '%s' (ieee=%s)",
                        device_name,
                        ieee,
                    )

                    return self.async_create_entry(
                        title=device_name,
                        data={
                            "device_name": device_name,
                            "ieee": ieee,
                        },
                    )

        schema = vol.Schema(
            {
                vol.Required(CONF_DEVICE_ID): selector.DeviceSelector(
                    selector.DeviceSelectorConfig(integration="mqtt"),
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
