from __future__ import annotations

from dataclasses import dataclass, field

from .alarm import AlarmSettings
from .manual import ManualSettings
from .plan import Plan
from .seasonal import SeasonalSettings
from .weather import WeatherSettings


@dataclass(slots=True)
class Device:

    ieee: str = ""

    model: str = ""

    firmware: str = ""

    battery: int = 0

    linkquality: int = 0

    state: str = "OFF"

    plan: Plan = field(
        default_factory=Plan,
    )

    manual: ManualSettings = field(
        default_factory=ManualSettings,
    )

    weather: WeatherSettings = field(
        default_factory=WeatherSettings,
    )

    seasonal: SeasonalSettings = field(
        default_factory=SeasonalSettings,
    )

    alarm: AlarmSettings = field(
        default_factory=AlarmSettings,
    )

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "Device":

        device = cls()

        info = data.get(
            "device",
            {},
        )

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

        if "irrigation_plan_settings" in data:

            device.plan = Plan.from_dict(
                data["irrigation_plan_settings"]
            )

        if "manual_default_settings" in data:

            device.manual = ManualSettings.from_dict(
                data["manual_default_settings"]
            )

        if "weather_based_adjustment" in data:

            device.weather = WeatherSettings.from_dict(
                data["weather_based_adjustment"]
            )

        if "seasonal_watering_adjustment" in data:

            device.seasonal = SeasonalSettings.from_dict(
                data["seasonal_watering_adjustment"]
            )

        if "valve_alarm_settings" in data:

            device.alarm = AlarmSettings.from_dict(
                data["valve_alarm_settings"]
            )

        return device