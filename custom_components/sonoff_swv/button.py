from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta

from homeassistant.components.button import (
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import (
    AddEntitiesCallback,
)

from .const import DOMAIN
from .coordinator import (
    HISTORY_PERIOD_24_HOURS,
    HISTORY_PERIOD_30_DAYS,
    HISTORY_PERIOD_180_DAYS,
    SonoffSWVCoordinator,
)
from .entity import SonoffSWVEntity


@dataclass(frozen=True)
class SonoffSWVButtonDescription(
    ButtonEntityDescription,
):
    """Description for Sonoff SWV buttons."""

    command: str = ""


BUTTONS = (
    SonoffSWVButtonDescription(
        key="read_irrigation_history",
        name="Read irrigation history",
        command="read_swvzf_records",
        icon="mdi:history",
    ),
    SonoffSWVButtonDescription(
        key="irrigation_plan_report",
        name="Irrigation plan report",
        command="irrigation_plan_report",
    ),
    SonoffSWVButtonDescription(
        key="irrigation_plan_remove",
        name="Irrigation plan remove",
        command="irrigation_plan_remove",
    ),
    SonoffSWVButtonDescription(
        key="irrigation_plan_settings",
        name="Irrigation plan settings",
        command="irrigation_plan_settings",
    ),
)


HISTORY_PERIOD_DAYS = {
    HISTORY_PERIOD_24_HOURS: 1,
    HISTORY_PERIOD_30_DAYS: 30,
    HISTORY_PERIOD_180_DAYS: 180,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sonoff SWV buttons."""

    coordinator: SonoffSWVCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        SonoffSWVButton(
            coordinator,
            description,
        )
        for description in BUTTONS
    )


class SonoffSWVButton(
    SonoffSWVEntity,
    ButtonEntity,
):
    """Sonoff SWV button entity."""

    entity_description: SonoffSWVButtonDescription

    def __init__(
        self,
        coordinator: SonoffSWVCoordinator,
        description: SonoffSWVButtonDescription,
    ) -> None:
        super().__init__(
            coordinator,
        )

        self.entity_description = description

        self._attr_unique_id = f"{coordinator.device_name}_" f"{description.key}"

    async def async_press(
        self,
    ) -> None:
        """Execute MQTT command."""

        if self.entity_description.key != "read_irrigation_history":
            await self.coordinator.publish_command(
                self.entity_description.command,
            )
            return

        period = self.coordinator.irrigation_history_period

        days = HISTORY_PERIOD_DAYS.get(
            period,
        )

        if days is None:
            return

        now = datetime.now().astimezone()

        today = now.date()

        # The requested day is included.
        #
        # 24_hours:
        #   today 00:00:00 -> today 23:59:59
        #
        # 30_days:
        #   today - 29 days -> today
        #
        # 180_days:
        #   today - 179 days -> today
        start_date = today - timedelta(
            days=days - 1,
        )

        end_date = today

        tzinfo = now.tzinfo

        start = datetime.combine(
            start_date,
            time(
                0,
                0,
                0,
            ),
            tzinfo=tzinfo,
        )

        end = datetime.combine(
            end_date,
            time(
                23,
                59,
                59,
            ),
            tzinfo=tzinfo,
        )

        payload = {
            "type": period,
            "start": start.isoformat(),
            "end": end.isoformat(),
        }

        await self.coordinator.publish_command(
            self.entity_description.command,
            payload,
        )
