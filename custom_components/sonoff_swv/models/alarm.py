from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AlarmSettings:
    """Impostazioni allarmi."""

    enable_alarm_water_leak: bool = False

    enable_alarm_water_shortage: bool = False

    enable_water_leak_auto_close: bool = False

    enable_water_shortage_auto_close: bool = False

    enable_frost_protection: bool = False

    alarm_water_leak_duration: int = 0

    alarm_water_shortage_duration: int = 0

    set_frost_temperature: int = 5

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "AlarmSettings":

        return cls(

            enable_alarm_water_leak=data.get(
                "enable_alarm_water_leak",
                False,
            ),

            enable_alarm_water_shortage=data.get(
                "enable_alarm_water_shortage",
                False,
            ),

            enable_water_leak_auto_close=data.get(
                "enable_water_leak_auto_close",
                False,
            ),

            enable_water_shortage_auto_close=data.get(
                "enable_water_shortage_auto_close",
                False,
            ),

            enable_frost_protection=data.get(
                "enable_frost_protection",
                False,
            ),

            alarm_water_leak_duration=data.get(
                "alarm_water_leak_duration",
                0,
            ),

            alarm_water_shortage_duration=data.get(
                "alarm_water_shortage_duration",
                0,
            ),

            set_frost_temperature=data.get(
                "set_frost_temperature",
                5,
            ),

        )

    def to_dict(self) -> dict:

        return {

            "enable_alarm_water_leak": self.enable_alarm_water_leak,

            "enable_alarm_water_shortage": self.enable_alarm_water_shortage,

            "enable_water_leak_auto_close": self.enable_water_leak_auto_close,

            "enable_water_shortage_auto_close": self.enable_water_shortage_auto_close,

            "enable_frost_protection": self.enable_frost_protection,

            "alarm_water_leak_duration": self.alarm_water_leak_duration,

            "alarm_water_shortage_duration": self.alarm_water_shortage_duration,

            "set_frost_temperature": self.set_frost_temperature,

        }