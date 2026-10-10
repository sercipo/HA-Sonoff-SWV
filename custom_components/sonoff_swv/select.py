from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.select import (
    SelectEntity,
    SelectEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import (
    AddEntitiesCallback,
)
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN
from .coordinator import (
    DEFAULT_HISTORY_PERIOD,
    HISTORY_PERIODS,
    SonoffSWVCoordinator,
)
from .coordinator import NOTIFY_CHANNEL_PLATFORM
from .entity import SonoffSWVEntity
from .entity_resolver import find_mqtt_entity
from .entity_setup import async_add_entities_after_start


@dataclass(frozen=True)
class SonoffSWVSelectDescription(
    SelectEntityDescription,
):
    """Description for Sonoff SWV select entities."""

    options: tuple[str, ...] = ()


HISTORY_PERIOD_OPTIONS = {
    "24_hours": "24 hours",
    "30_days": "30 days",
    "180_days": "180 days",
}


SELECTS = (
    SonoffSWVSelectDescription(
        key="irrigation_plan_mode",
        name="Irrigation plan mode",
        options=(
            "duration",
            "capacity",
            "duration_with_interval",
        ),
    ),
    SonoffSWVSelectDescription(
        key="irrigation_plan_loop_type",
        name="Irrigation plan loop type",
        options=(
            "odd_days",
            "even_days",
            "day_interval",
            "weekdays",
        ),
    ),
    SonoffSWVSelectDescription(
        key="manual_irrigation_mode",
        name="Manual irrigation mode",
        options=(
            "duration",
            "capacity",
        ),
    ),
    SonoffSWVSelectDescription(
        key="irrigation_history_period",
        name="Irrigation history period",
        icon="mdi:calendar-range",
        options=(
            "24 hours",
            "30 days",
            "180 days",
        ),
    ),
)

NOTIFY_SELECTS = (
    SonoffSWVSelectDescription(key="notify_channel", name="Notify channel"),
    SonoffSWVSelectDescription(key="notify_target", name="Notify target"),
    SonoffSWVSelectDescription(key="notify_warning_minutes", name="Notify warning minutes"),
)

WARNING_MINUTES_OPTIONS = ("5", "10", "15", "30", "60", "120")

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sonoff SWV select entities."""

    coordinator: SonoffSWVCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities_after_start(
        hass,
        async_add_entities,
        coordinator,
        SELECTS,
        SonoffSWVSelect,
        "select",
    )

    async_add_entities_after_start(
        hass,
        async_add_entities,
        coordinator,
        NOTIFY_SELECTS,
        SonoffSWVNotifySelect,
        "select",
    )


class SonoffSWVSelect(
    SonoffSWVEntity,
    SelectEntity,
):
    """Sonoff SWV select entity."""

    entity_description: SonoffSWVSelectDescription

    def __init__(
        self,
        coordinator: SonoffSWVCoordinator,
        description: SonoffSWVSelectDescription,
    ) -> None:
        super().__init__(
            coordinator,
        )

        self.entity_description = description

        self._attr_unique_id = f"{coordinator.device_name}_" f"{description.key}"

        self._attr_options = list(description.options)

        if description.key == "irrigation_history_period":
            current_period = coordinator.irrigation_history_period

            if current_period not in HISTORY_PERIOD_OPTIONS:
                current_period = DEFAULT_HISTORY_PERIOD

            self._attr_current_option = HISTORY_PERIOD_OPTIONS[current_period]

    @property
    def current_option(
        self,
    ) -> str | None:
        """Return the currently selected option."""

        if self.entity_description.key == "irrigation_history_period":
            return self._attr_current_option

        value = self.get_value()

        if value in self.options:
            return value

        return None

    async def async_select_option(
        self,
        option: str,
    ) -> None:
        """Handle select option."""

        if self.entity_description.key == "irrigation_history_period":
            period = next(
                (
                    key
                    for key, label in HISTORY_PERIOD_OPTIONS.items()
                    if label == option
                ),
                None,
            )

            if period is None:
                return

            await self.coordinator.async_set_history_period(
                period,
            )

            self._attr_current_option = option

            self.async_write_ha_state()
            return

        if option not in self.options:
            return

        setattr(
            self.coordinator.device,
            self.entity_description.key,
            option,
        )

        await self.coordinator.publish_attribute(
            self.entity_description.key,
        )

        self.async_write_ha_state()


class SonoffSWVNotifySelect(SonoffSWVSelect):
    """Selezioni locali delle notifiche: non scrivono sul device."""

    @property
    def _setting(self) -> str:
        return self.entity_description.key.removeprefix("notify_")

    def _channel_labels(self) -> dict[str, str]:
        return {
            "telegram": self.coordinator.text("telegram"),
            "app": self.coordinator.text("app"),
        }

    def _target_choices(self) -> dict[str, str]:
        """Nome leggibile -> entity_id dei destinatari del tipo scelto."""
        platform = NOTIFY_CHANNEL_PLATFORM.get(self.coordinator.notify_channel())
        if platform is None:
            return {}

        registry = er.async_get(self.hass)

        def _label(entry) -> str:
            return (entry.name or entry.original_name or entry.entity_id).strip()

        entries = sorted(
            (
                entry
                for entry in registry.entities.values()
                if entry.platform == platform
                and entry.entity_id.startswith("notify.")
            ),
            key=lambda entry: _label(entry).lower(),
        )

        choices: dict[str, str] = {}
        for entry in entries:
            label = _label(entry)
            if label in choices:
                label = f"{label} ({entry.entity_id})"
            choices[label] = entry.entity_id
        return choices

    @property
    def available(self) -> bool:
        if not super().available:
            return False
        if self._setting == "channel":
            return True
        if self._setting == "target":
            return self.coordinator.notify_channel() is not None
        return bool(self.coordinator.notify_setting("target"))

    @property
    def options(self) -> list[str]:
        none = self.coordinator.text("none")
        if self._setting == "channel":
            return [none, *self._channel_labels().values()]
        if self._setting == "target":
            return [none, *self._target_choices()]
        return list(WARNING_MINUTES_OPTIONS)

    @property
    def current_option(self) -> str:
        none = self.coordinator.text("none")
        if self._setting == "channel":
            return self._channel_labels().get(
                self.coordinator.notify_channel(), none
            )
        value = self.coordinator.notify_setting(self._setting)
        if self._setting == "target":
            if not value:
                return none
            for label, entity_id in self._target_choices().items():
                if entity_id == value:
                    return label
            return none
        return str(value) if str(value) in self.options else "15"

    async def async_select_option(self, option: str) -> None:
        if self._setting == "channel":
            value = next(
                (k for k, label in self._channel_labels().items() if label == option),
                None,
            )
        elif self._setting == "target":
            value = self._target_choices().get(option)
        else:
            value = int(option)
        await self.coordinator.async_set_notify_setting(self._setting, value)