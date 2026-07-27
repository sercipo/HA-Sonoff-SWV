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

        device.update_from_dict(data)

        return device

    def update_from_dict(
        self,
        data: dict,
    ) -> None:

        info = data.get(
            "device",
            {},
        )

        self.ieee = info.get(
            "ieeeAddr",
            "",
        )

        self.model = info.get(
            "model",
            "",
        )

        self.firmware = info.get(
            "softwareBuildID",
            "",
        )

        self.battery = data.get(
            "battery",
            self.battery,
        )

        self.linkquality = data.get(
            "linkquality",
            self.linkquality,
        )

        self.state = data.get(
            "state",
            self.state,
        )

        if "irrigation_plan_settings" in data:

            self.plan.update_from_dict(
                data["irrigation_plan_settings"]
            )

        if "manual_default_settings" in data:

            self.manual.update_from_dict(
                data["manual_default_settings"]
            )

        if "weather_based_adjustment" in data:

            self.weather.update_from_dict(
                data["weather_based_adjustment"]
            )

        if "seasonal_watering_adjustment" in data:

            self.seasonal.update_from_dict(
                data["seasonal_watering_adjustment"]
            )

        if "valve_alarm_settings" in data:

            self.alarm.update_from_dict(
                data["valve_alarm_settings"]
            )

    def to_dict(
        self,
    ) -> dict:

        return {

            "device": {

                "ieeeAddr": self.ieee,

                "model": self.model,

                "softwareBuildID": self.firmware,

            },

            "battery": self.battery,

            "linkquality": self.linkquality,

            "state": self.state,

            "irrigation_plan_settings":
                self.plan.to_dict(),

            "manual_default_settings":
                self.manual.to_dict(),

            "weather_based_adjustment":
                self.weather.to_dict(),

            "seasonal_watering_adjustment":
                self.seasonal.to_dict(),

            "valve_alarm_settings":
                self.alarm.to_dict(),

        }