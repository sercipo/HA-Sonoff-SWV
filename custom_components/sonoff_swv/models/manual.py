from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ManualSettings:
    """Impostazioni dell'irrigazione manuale."""

    irrigation_mode: str = "capacity"

    irrigation_amount: int = 0

    irrigation_amount_unit: str = "liter"

    irrigation_duration: int = 0

    irrigation_total_duration: int = 0

    interval_duration: int = 0

    fail_safe: int = 0

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "ManualSettings":

        return cls(

            irrigation_mode=data.get(
                "irrigation_mode",
                "capacity",
            ),

            irrigation_amount=data.get(
                "irrigation_amount",
                0,
            ),

            irrigation_amount_unit=data.get(
                "irrigation_amount_unit",
                "liter",
            ),

            irrigation_duration=data.get(
                "irrigation_duration",
                0,
            ),

            irrigation_total_duration=data.get(
                "irrigation_total_duration",
                0,
            ),

            interval_duration=data.get(
                "interval_duration",
                0,
            ),

            fail_safe=data.get(
                "fail_safe",
                0,
            ),

        )

    def to_dict(self) -> dict:

        return {

            "irrigation_mode": self.irrigation_mode,

            "irrigation_amount": self.irrigation_amount,

            "irrigation_amount_unit": self.irrigation_amount_unit,

            "irrigation_duration": self.irrigation_duration,

            "irrigation_total_duration": self.irrigation_total_duration,

            "interval_duration": self.interval_duration,

            "fail_safe": self.fail_safe,

        }