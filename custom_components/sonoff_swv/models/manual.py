from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass


@dataclass(slots=True)
class ManualSettings:

    fail_safe: int = 6

    irrigation_amount: int = 10

    irrigation_amount_unit: str = "liter"

    irrigation_duration: int = 0

    irrigation_mode: str = "capacity"

    irrigation_total_duration: int = 1

    interval_duration: int = 0

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "ManualSettings":

        return cls(

            fail_safe=data.get(
                "fail_safe",
                6,
            ),

            irrigation_amount=data.get(
                "irrigation_amount",
                10,
            ),

            irrigation_amount_unit=data.get(
                "irrigation_amount_unit",
                "liter",
            ),

            irrigation_duration=data.get(
                "irrigation_duration",
                0,
            ),

            irrigation_mode=data.get(
                "irrigation_mode",
                "capacity",
            ),

            irrigation_total_duration=data.get(
                "irrigation_total_duration",
                1,
            ),

            interval_duration=data.get(
                "interval_duration",
                0,
            ),

        )

    def to_dict(self) -> dict:

        return {
            "fail_safe": self.fail_safe,
            "irrigation_amount": self.irrigation_amount,
            "irrigation_amount_unit": self.irrigation_amount_unit,
            "irrigation_duration": self.irrigation_duration,
            "irrigation_mode": self.irrigation_mode,
            "irrigation_total_duration": self.irrigation_total_duration,
            "interval_duration": self.interval_duration,
        }