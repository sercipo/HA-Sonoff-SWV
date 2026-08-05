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
    "select",
    "button",
    "binary_sensor",

]


async def async_setup(
    hass: HomeAssistant,
    config,
) -> bool:
    """Set up Sonoff SWV."""

    hass.data.setdefault(
        DOMAIN,
        {},
    )

    return True



async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up Sonoff SWV from config entry."""

    print("SONOFF SETUP ENTRY START")

    coordinator = SonoffSWVCoordinator(
        hass,
        entry.data["device_name"],
    )

    print(
        "SONOFF COORDINATOR CREATED:",
        entry.data["device_name"],
    )


    await coordinator.async_initialize()

    print(
        "SONOFF COORDINATOR INITIALIZED"
    )


    hass.data[DOMAIN][
        entry.entry_id
    ] = coordinator


    await coordinator.async_start()

    print(
        "SONOFF MQTT SUBSCRIBE STARTED"
    )


    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )


    print(
        "SONOFF PLATFORMS LOADED"
    )


    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Unload Sonoff SWV."""

    coordinator = hass.data[DOMAIN][
        entry.entry_id
    ]


    await coordinator.async_stop()


    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )


    if unload_ok:

        hass.data[DOMAIN].pop(
            entry.entry_id
        )


    return unload_ok