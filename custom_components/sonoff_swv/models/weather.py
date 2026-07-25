from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WeatherSettings:
    """Regolazioni meteo del Sonoff."""

    enable_rain_delay: bool = False

    enable_humidity_delay: bool = False

    enable_frost_delay: bool = False

    rain_probability_threshold: int = 0

    humidity_delay_threshold: int = 0

    frost_temperature_threshold: int = 0

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "WeatherSettings":

        return cls(

            enable_rain_delay=data.get(
                "enable_rain_delay",
                False,
            ),

            enable_humidity_delay=data.get(
                "enable_humidity_delay",
                False,
            ),

            enable_frost_delay=data.get(
                "enable_frost_delay",
                False,
            ),

            rain_probability_threshold=data.get(
                "rain_probability_threshold",
                0,
            ),

            humidity_delay_threshold=data.get(
                "humidity_delay_threshold",
                0,
            ),

            frost_temperature_threshold=data.get(
                "frost_temperature_threshold",
                0,
            ),

        )

    def to_dict(self) -> dict:

        return {

            "enable_rain_delay": self.enable_rain_delay,

            "enable_humidity_delay": self.enable_humidity_delay,

            "enable_frost_delay": self.enable_frost_delay,

            "rain_probability_threshold": self.rain_probability_threshold,

            "humidity_delay_threshold": self.humidity_delay_threshold,

            "frost_temperature_threshold": self.frost_temperature_threshold,

        }