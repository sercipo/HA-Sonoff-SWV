from __future__ import annotations

from homeassistant.helpers.storage import Store

from .const import STORAGE_KEY, STORAGE_VERSION


class SonoffStorage:

    def __init__(self, hass):
        self._store = Store(
            hass,
            STORAGE_VERSION,
            STORAGE_KEY,
        )

    async def load(self):
        data = await self._store.async_load()

        if data is None:
            data = {
                "original": {},
                "user": {}
            }

        return data

    async def save(self, data):
        await self._store.async_save(data)