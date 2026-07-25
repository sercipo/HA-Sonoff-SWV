from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries

from .const import DOMAIN, CONF_DEVICE, DEFAULT_DEVICE


class SonoffSWVConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    async def async_step_user(self, user_input=None):

        if user_input is not None:

            return self.async_create_entry(
                title=user_input[CONF_DEVICE],
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_DEVICE,
                    default=DEFAULT_DEVICE,
                ): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
        )