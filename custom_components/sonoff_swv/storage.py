from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import (
    STORAGE_KEY,
    STORAGE_VERSION,
)


class SonoffStorage:
    """Persistent storage for Sonoff SWV."""


    def __init__(
        self,
        hass: HomeAssistant,
    ) -> None:

        self._store = Store(
            hass,
            STORAGE_VERSION,
            STORAGE_KEY,
        )



    async def load(
        self,
    ) -> dict[str, Any]:
        """Load stored data."""


        data = await self._store.async_load()


        if data is None:

            return {
                "device": {},
            }


        return data



    async def save(
        self,
        data: dict[str, Any],
    ) -> None:
        """Save stored data."""


        await self._store.async_save(
            data
        )