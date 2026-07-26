from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field


@dataclass(slots=True)
class Plan:

    plan_index: int = 0

    create_datetime: str = ""

    enable_date: str = ""

    enable_state: bool = False

    fail_safe: int = 6

    irrigation_amount: int = 0

    irrigation_amount_unit: str = "liter"

    irrigation_duration: int | None = None

    irrigation_total_duration: int | None = None

    irrigation_mode: str = "capacity"

    interval_duration: int | None = None

    loop_type_mode: str = "day_interval"

    loop_type_interval_days: int = 1

    loop_type_week_days: dict[str, bool] = field(
        default_factory=lambda: {
            "monday": False,
            "tuesday": False,
            "wednesday": False,
            "thursday": False,
            "friday": False,
            "saturday": False,
            "sunday": False,
        }
    )

    start_time: str = "00:00"

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "Plan":

        return cls(
            plan_index=data.get("plan_index", 0),
            create_datetime=data.get("create_datetime", ""),
            enable_date=data.get("enable_date", ""),
            enable_state=data.get("enable_state", False),
            fail_safe=data.get("fail_safe", 6),
            irrigation_amount=data.get("irrigation_amount", 0),
            irrigation_amount_unit=data.get(
                "irrigation_amount_unit",
                "liter",
            ),
            irrigation_duration=data.get(
                "irrigation_duration"
            ),
            irrigation_total_duration=data.get(
                "irrigation_total_duration"
            ),
            irrigation_mode=data.get(
                "irrigation_mode",
                "capacity",
            ),
            interval_duration=data.get(
                "interval_duration"
            ),
            loop_type_mode=data.get(
                "loop_type_mode",
                "day_interval",
            ),
            loop_type_interval_days=data.get(
                "loop_type_interval_days",
                1,
            ),
            loop_type_week_days=deepcopy(
                data.get(
                    "loop_type_week_days",
                    {},
                )
            ),
            start_time=data.get(
                "start_time",
                "00:00",
            ),
        )

    def to_dict(self) -> dict:

        return {
            "plan_index": self.plan_index,
            "create_datetime": self.create_datetime,
            "enable_date": self.enable_date,
            "enable_state": self.enable_state,
            "fail_safe": self.fail_safe,
            "irrigation_amount": self.irrigation_amount,
            "irrigation_amount_unit": self.irrigation_amount_unit,
            "irrigation_duration": self.irrigation_duration,
            "irrigation_total_duration": self.irrigation_total_duration,
            "irrigation_mode": self.irrigation_mode,
            "interval_duration": self.interval_duration,
            "loop_type_mode": self.loop_type_mode,
            "loop_type_interval_days": self.loop_type_interval_days,
            "loop_type_week_days": deepcopy(
                self.loop_type_week_days
            ),
            "start_time": self.start_time,
        }

    def clone(self) -> "Plan":

        return Plan.from_dict(
            self.to_dict()
        )

    def update_from_dict(
        self,
        data: dict,
    ) -> None:

        updated = Plan.from_dict(data)

        self.plan_index = updated.plan_index
        self.create_datetime = updated.create_datetime
        self.enable_date = updated.enable_date
        self.enable_state = updated.enable_state
        self.fail_safe = updated.fail_safe
        self.irrigation_amount = updated.irrigation_amount
        self.irrigation_amount_unit = updated.irrigation_amount_unit
        self.irrigation_duration = updated.irrigation_duration
        self.irrigation_total_duration = updated.irrigation_total_duration
        self.irrigation_mode = updated.irrigation_mode
        self.interval_duration = updated.interval_duration
        self.loop_type_mode = updated.loop_type_mode
        self.loop_type_interval_days = updated.loop_type_interval_days
        self.loop_type_week_days = deepcopy(
            updated.loop_type_week_days
        )
        self.start_time = updated.start_time