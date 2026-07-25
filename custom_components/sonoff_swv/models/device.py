from __future__ import annotations

from dataclasses import dataclass, field

from .alarm import AlarmSettings
from .manual import ManualSettings
from .plan import IrrigationPlan
from .seasonal import SeasonalSettings
from .weather import WeatherSettings


@dataclass
class SonoffDevice:
    """Rappresenta completamente un Sonoff SWV."""

    ieee: str = ""
    model: str = ""
    firmware: str = ""

    battery: int = 0
    linkquality: int = 0
    state: str = "OFF"

    plans: list[IrrigationPlan] = field(default_factory=list)

    manual: ManualSettings = field(
        default_factory=ManualSettings
    )

    alarms: AlarmSettings = field(
        default_factory=AlarmSettings
    )

    weather: WeatherSettings = field(
        default_factory=WeatherSettings
    )

    seasonal: SeasonalSettings = field(
        default_factory=SeasonalSettings
    )

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "SonoffDevice":

        device = cls()

        info = data.get("device", {})

        device.ieee = info.get(
            "ieeeAddr",
            "",
        )

        device.model = info.get(
            "model",
            "",
        )

        device.firmware = info.get(
            "softwareBuildID",
            "",
        )

        device.battery = data.get(
            "battery",
            0,
        )

        device.linkquality = data.get(
            "linkquality",
            0,
        )

        device.state = data.get(
            "state",
            "OFF",
        )

        # Piano attualmente restituito da Zigbee2MQTT
        plan = data.get("irrigation_plan_settings")

        if plan is not None:
            device.plans.append(
                IrrigationPlan.from_dict(plan)
            )

        # Impostazioni manuali
        device.manual = ManualSettings.from_dict(
            data.get(
                "manual_default_settings",
                {}
            )
        )

        # Allarmi
        device.alarms = AlarmSettings.from_dict(
            data.get(
                "valve_alarm_settings",
                {}
            )
        )

        # Meteo
        device.weather = WeatherSettings.from_dict(
            data.get(
                "weather_based_adjustment",
                {}
            )
        )

        # Stagionalità
        device.seasonal = SeasonalSettings.from_dict(
            data.get(
                "seasonal_watering_adjustment",
                {}
            )
        )

        return device