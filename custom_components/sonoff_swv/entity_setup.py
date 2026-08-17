from __future__ import annotations

from collections.abc import Callable
from typing import Any

from homeassistant.core import Event, HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_call_later

from .entity_resolver import find_mqtt_entity


def async_add_entities_after_start(
    hass: HomeAssistant,
    async_add_entities: AddEntitiesCallback,
    coordinator: Any,
    descriptions: tuple[Any, ...],
    entity_factory: Callable[[Any, Any], Any],
) -> None:
    """Add only entities that are not already provided by MQTT."""

    async def _add_entities(
        _event: Event | None = None,
    ) -> None:
        ieee = coordinator.device.ieee

        entities = []

        for description in descriptions:
            if find_mqtt_entity(
                hass,
                ieee,
                description.key,
            ):
                continue

            entities.append(
                entity_factory(
                    coordinator,
                    description,
                )
            )

        if entities:
            async_add_entities(entities)

    if hass.is_running:
        async_call_later(
            hass,
            0,
            _add_entities,
        )
    else:
        hass.bus.async_listen_once(
            "homeassistant_started",
            _add_entities,
        )