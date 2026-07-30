from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class Device:
    """Flat model for Sonoff SWV-ZFE device."""

    ieee: str = ""

    manufacturer: str = "SONOFF"

    model: str = ""

    firmware: str = ""

    hardware: str = ""

    friendly_name: str = ""


    battery: int | None = None

    linkquality: int | None = None


    state: str = "OFF"

    child_lock: bool = False


    rain_delay: Any = None


    irrigation_schedule_status: dict[str, Any] | None = None

    real_time_irrigation_volume: int | None = None

    real_time_irrigation_duration: int | None = None


    daily_irrigation_volume: int | None = None

    daily_irrigation_duration: int | None = None


    hour_irrigation_volume: int | None = None

    hour_irrigation_duration: int | None = None


    irrigation_plan_enabled: bool = False


    irrigation_plan_amount: int | None = None

    irrigation_plan_mode: str | None = None

    irrigation_plan_duration: int | None = None

    irrigation_plan_total_duration: int | None = None

    irrigation_plan_interval_duration: int | None = None

    irrigation_plan_interval_days: int | None = None

    irrigation_plan_fail_safe: int | None = None

    irrigation_plan_start_time: str | None = None


    irrigation_plan_monday: bool = False

    irrigation_plan_tuesday: bool = False

    irrigation_plan_wednesday: bool = False

    irrigation_plan_thursday: bool = False

    irrigation_plan_friday: bool = False

    irrigation_plan_saturday: bool = False

    irrigation_plan_sunday: bool = False


    manual_irrigation_amount: int | None = None

    manual_irrigation_mode: str | None = None

    manual_irrigation_duration: int | None = None

    manual_irrigation_total_duration: int | None = None

    manual_interval_duration: int | None = None

    manual_fail_safe: int | None = None


    enable_alarm_water_shortage: bool = False

    enable_alarm_water_leak: bool = False

    enable_water_shortage_auto_close: bool = False

    enable_water_leak_auto_close: bool = False

    def update_from_z2m_payload(
        self,
        payload: dict[str, Any],
    ) -> None:
        """Update Device from Zigbee2MQTT payload."""


        device_info = payload.get(
            "device",
            {},
        )


        self.ieee = device_info.get(
            "ieeeAddr",
            self.ieee,
        )


        self.manufacturer = device_info.get(
            "manufacturerName",
            self.manufacturer,
        )


        self.model = device_info.get(
            "model",
            self.model,
        )


        self.firmware = device_info.get(
            "softwareBuildID",
            self.firmware,
        )


        self.hardware = device_info.get(
            "hardwareVersion",
            self.hardware,
        )


        self.friendly_name = device_info.get(
            "friendlyName",
            self.friendly_name,
        )



        direct_fields = (

            "battery",

            "linkquality",

            "state",

            "child_lock",

            "rain_delay",

            "irrigation_schedule_status",

            "real_time_irrigation_volume",

            "real_time_irrigation_duration",

            "daily_irrigation_volume",

            "daily_irrigation_duration",

            "hour_irrigation_volume",

            "hour_irrigation_duration",
        )


        for field_name in direct_fields:

            if field_name in payload:

                setattr(
                    self,
                    field_name,
                    payload[field_name],
                )



        plan = payload.get(
            "irrigation_plan_settings",
            {},
        )


        if plan:


            self.irrigation_plan_enabled = plan.get(
                "enable_state",
                self.irrigation_plan_enabled,
            )


            self.irrigation_plan_amount = plan.get(
                "irrigation_amount",
                self.irrigation_plan_amount,
            )


            self.irrigation_plan_mode = plan.get(
                "irrigation_mode",
                self.irrigation_plan_mode,
            )


            self.irrigation_plan_duration = plan.get(
                "irrigation_duration",
                self.irrigation_plan_duration,
            )


            self.irrigation_plan_total_duration = plan.get(
                "irrigation_total_duration",
                self.irrigation_plan_total_duration,
            )


            self.irrigation_plan_interval_duration = plan.get(
                "interval_duration",
                self.irrigation_plan_interval_duration,
            )


            self.irrigation_plan_interval_days = plan.get(
                "loop_type_interval_days",
                self.irrigation_plan_interval_days,
            )


            self.irrigation_plan_fail_safe = plan.get(
                "fail_safe",
                self.irrigation_plan_fail_safe,
            )


            self.irrigation_plan_start_time = plan.get(
                "start_time",
                self.irrigation_plan_start_time,
            )



            week_days = plan.get(
                "loop_type_week_days",
                {},
            )


            self.irrigation_plan_monday = week_days.get(
                "monday",
                self.irrigation_plan_monday,
            )


            self.irrigation_plan_tuesday = week_days.get(
                "tuesday",
                self.irrigation_plan_tuesday,
            )


            self.irrigation_plan_wednesday = week_days.get(
                "wednesday",
                self.irrigation_plan_wednesday,
            )


            self.irrigation_plan_thursday = week_days.get(
                "thursday",
                self.irrigation_plan_thursday,
            )


            self.irrigation_plan_friday = week_days.get(
                "friday",
                self.irrigation_plan_friday,
            )


            self.irrigation_plan_saturday = week_days.get(
                "saturday",
                self.irrigation_plan_saturday,
            )


            self.irrigation_plan_sunday = week_days.get(
                "sunday",
                self.irrigation_plan_sunday,
            )

        manual = payload.get(
            "manual_default_settings",
            {},
        )


        if manual:


            self.manual_irrigation_amount = manual.get(
                "irrigation_amount",
                self.manual_irrigation_amount,
            )


            self.manual_irrigation_mode = manual.get(
                "irrigation_mode",
                self.manual_irrigation_mode,
            )


            self.manual_irrigation_duration = manual.get(
                "irrigation_duration",
                self.manual_irrigation_duration,
            )


            self.manual_irrigation_total_duration = manual.get(
                "irrigation_total_duration",
                self.manual_irrigation_total_duration,
            )


            self.manual_interval_duration = manual.get(
                "interval_duration",
                self.manual_interval_duration,
            )


            self.manual_fail_safe = manual.get(
                "fail_safe",
                self.manual_fail_safe,
            )



        alarm = payload.get(
            "valve_alarm_settings",
            {},
        )


        if alarm:


            self.enable_alarm_water_shortage = alarm.get(
                "enable_alarm_water_shortage",
                self.enable_alarm_water_shortage,
            )


            self.enable_alarm_water_leak = alarm.get(
                "enable_alarm_water_leak",
                self.enable_alarm_water_leak,
            )


            self.enable_water_shortage_auto_close = alarm.get(
                "enable_water_shortage_auto_close",
                self.enable_water_shortage_auto_close,
            )


            self.enable_water_leak_auto_close = alarm.get(
                "enable_water_leak_auto_close",
                self.enable_water_leak_auto_close,
            )

    def to_storage_dict(
        self,
    ) -> dict[str, Any]:
        """Convert Device to storage dictionary."""

        return asdict(
            self
        )



    @classmethod
    def from_storage_dict(
        cls,
        data: dict[str, Any],
    ) -> "Device":
        """Restore Device from storage dictionary."""

        device = cls()


        for key, value in data.items():

            if hasattr(
                device,
                key,
            ):

                setattr(
                    device,
                    key,
                    value,
                )


        return device