from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import SonoffSWVCoordinator

PLATFORMS = [
    "sensor",
    "number",
    "switch",
    "time",
]


async def async_setup(
    hass: HomeAssistant,
    config,
) -> bool:

    hass.data.setdefault(DOMAIN, {})

    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:

    coordinator = SonoffSWVCoordinator(
        hass,
        entry.data["device_name"],
    )

    await coordinator.async_initialize()

    await coordinator.async_start()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:

    coordinator = hass.data[DOMAIN][entry.entry_id]

    await coordinator.async_stop()

    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok