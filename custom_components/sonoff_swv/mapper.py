from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models.device import Device


@dataclass(frozen=True)
class DeviceMapping:
    """Map Device attribute to Zigbee2MQTT payload."""

    attribute: str
    mqtt_key: str
    group: str | None = None
    subgroup: str | None = None


MAPPINGS = (
    DeviceMapping(
        "state",
        "state",
    ),
    DeviceMapping(
        "child_lock",
        "child_lock",
    ),
    DeviceMapping(
        "rain_delay",
        "rain_delay",
    ),
    DeviceMapping(
        "rain_delay_end_datetime",
        "rain_delay_end_datetime",
    ),
    DeviceMapping(
        "valve_abnormal_state",
        "valve_abnormal_state",
    ),
    #
    # Irrigation plan settings
    #
    DeviceMapping(
        "irrigation_plan_enabled",
        "enable_state",
        "irrigation_plan_settings",
    ),
    DeviceMapping(
        "irrigation_plan_index",
        "plan_index",
        "irrigation_plan_settings",
    ),
    DeviceMapping(
        "irrigation_plan_amount",
        "irrigation_amount",
        "irrigation_plan_settings",
    ),
    DeviceMapping(
        "irrigation_plan_amount_unit",
        "irrigation_amount_unit",
        "irrigation_plan_settings",
    ),
    DeviceMapping(
        "irrigation_plan_mode",
        "irrigation_mode",
        "irrigation_plan_settings",
    ),
    DeviceMapping(
        "irrigation_plan_duration",
        "irrigation_duration",
        "irrigation_plan_settings",
    ),
    DeviceMapping(
        "irrigation_plan_total_duration",
        "irrigation_total_duration",
        "irrigation_plan_settings",
    ),
    DeviceMapping(
        "irrigation_plan_interval_duration",
        "interval_duration",
        "irrigation_plan_settings",
    ),
    DeviceMapping(
        "irrigation_plan_fail_safe",
        "fail_safe",
        "irrigation_plan_settings",
    ),
    DeviceMapping(
        "irrigation_plan_interval_days",
        "loop_type_interval_days",
        "irrigation_plan_settings",
    ),
    DeviceMapping(
        "irrigation_plan_loop_type",
        "loop_type_mode",
        "irrigation_plan_settings",
    ),
    DeviceMapping(
        "irrigation_plan_start_time",
        "start_time",
        "irrigation_plan_settings",
    ),
    DeviceMapping(
        "irrigation_plan_create_datetime",
        "create_datetime",
        "irrigation_plan_settings",
    ),
    #
    # Week days
    #
    DeviceMapping(
        "irrigation_plan_monday",
        "monday",
        "irrigation_plan_settings",
        "loop_type_week_days",
    ),
    DeviceMapping(
        "irrigation_plan_tuesday",
        "tuesday",
        "irrigation_plan_settings",
        "loop_type_week_days",
    ),
    DeviceMapping(
        "irrigation_plan_wednesday",
        "wednesday",
        "irrigation_plan_settings",
        "loop_type_week_days",
    ),
    DeviceMapping(
        "irrigation_plan_thursday",
        "thursday",
        "irrigation_plan_settings",
        "loop_type_week_days",
    ),
    DeviceMapping(
        "irrigation_plan_friday",
        "friday",
        "irrigation_plan_settings",
        "loop_type_week_days",
    ),
    DeviceMapping(
        "irrigation_plan_saturday",
        "saturday",
        "irrigation_plan_settings",
        "loop_type_week_days",
    ),
    DeviceMapping(
        "irrigation_plan_sunday",
        "sunday",
        "irrigation_plan_settings",
        "loop_type_week_days",
    ),
    #
    # Irrigation plan report
    #
    DeviceMapping(
        "irrigation_plan_report",
        "irrigation_plan_report",
    ),
    DeviceMapping(
        "irrigation_schedule_status",
        "irrigation_schedule_status",
    ),
    #
    # Manual settings
    #
    DeviceMapping(
        "manual_irrigation_amount",
        "irrigation_amount",
        "manual_default_settings",
    ),
    DeviceMapping(
        "manual_irrigation_amount_unit",
        "irrigation_amount_unit",
        "manual_default_settings",
    ),
    DeviceMapping(
        "manual_irrigation_mode",
        "irrigation_mode",
        "manual_default_settings",
    ),
    DeviceMapping(
        "manual_irrigation_duration",
        "irrigation_duration",
        "manual_default_settings",
    ),
    DeviceMapping(
        "manual_irrigation_total_duration",
        "irrigation_total_duration",
        "manual_default_settings",
    ),
    DeviceMapping(
        "manual_interval_duration",
        "interval_duration",
        "manual_default_settings",
    ),
    DeviceMapping(
        "manual_fail_safe",
        "fail_safe",
        "manual_default_settings",
    ),
    #
    # Alarm settings
    #
    DeviceMapping(
        "enable_alarm_water_shortage",
        "enable_alarm_water_shortage",
        "valve_alarm_settings",
    ),
    DeviceMapping(
        "enable_alarm_water_leak",
        "enable_alarm_water_leak",
        "valve_alarm_settings",
    ),
    DeviceMapping(
        "enable_water_shortage_auto_close",
        "enable_water_shortage_auto_close",
        "valve_alarm_settings",
    ),
    DeviceMapping(
        "enable_water_leak_auto_close",
        "enable_water_leak_auto_close",
        "valve_alarm_settings",
    ),
    DeviceMapping(
        "enable_frost_protection",
        "enable_frost_protection",
        "valve_alarm_settings",
    ),
    DeviceMapping(
        "set_frost_temperature",
        "set_frost_temperature",
        "valve_alarm_settings",
    ),
    DeviceMapping(
        "alarm_water_leak_duration",
        "alarm_water_leak_duration",
        "valve_alarm_settings",
    ),
    DeviceMapping(
        "alarm_water_shortage_duration",
        "alarm_water_shortage_duration",
        "valve_alarm_settings",
    ),
    #
    # Weather adjustment
    #
    DeviceMapping(
        "enable_frost_delay",
        "enable_frost_delay",
        "weather_based_adjustment",
    ),
    DeviceMapping(
        "enable_humidity_delay",
        "enable_humidity_delay",
        "weather_based_adjustment",
    ),
    DeviceMapping(
        "enable_rain_delay",
        "enable_rain_delay",
        "weather_based_adjustment",
    ),
    DeviceMapping(
        "frost_temperature_threshold",
        "frost_temperature_threshold",
        "weather_based_adjustment",
    ),
    DeviceMapping(
        "humidity_delay_threshold",
        "humidity_delay_threshold",
        "weather_based_adjustment",
    ),
    DeviceMapping(
        "rain_probability_threshold",
        "rain_probability_threshold",
        "weather_based_adjustment",
    ),
    DeviceMapping(
        "weather_based_adjustment",
        "weather_based_adjustment",
    ),
)


def get_mapping(
    attribute: str,
) -> DeviceMapping | None:

    for mapping in MAPPINGS:

        if mapping.attribute == attribute:
            return mapping

    return None


def build_payload_for_attribute(
    device: Device,
    attribute: str,
) -> dict[str, Any]:

    mapping = get_mapping(
        attribute,
    )

    if mapping is None:
        return {}

    value = getattr(
        device,
        mapping.attribute,
        None,
    )

    #
    # Attributo diretto
    #
    # esempio:
    # {
    #   "state": "ON"
    # }
    #
    if mapping.group is None:

        return {mapping.mqtt_key: value}

    #
    # Gruppo senza sottogruppo
    #
    # esempio:
    # {
    #   "manual_default_settings": {
    #       "irrigation_duration": 1
    #   }
    # }
    #
    if mapping.subgroup is None:

        return {mapping.group: {mapping.mqtt_key: value}}

    #
    # Gruppo con sottogruppo
    #
    # esempio:
    # {
    #   "irrigation_plan_settings": {
    #       "loop_type_week_days": {
    #           "monday": true
    #       }
    #   }
    # }
    #
    return {mapping.group: {mapping.subgroup: {mapping.mqtt_key: value}}}


def build_payload_for_group(
    device: Device,
    group: str,
) -> dict[str, Any]:

    payload: dict[str, Any] = {}

    for mapping in MAPPINGS:

        if mapping.group != group:
            continue

        value = getattr(
            device,
            mapping.attribute,
            None,
        )

        if value is None:
            continue

        if mapping.subgroup:

            payload.setdefault(
                mapping.subgroup,
                {},
            )

            payload[mapping.subgroup][mapping.mqtt_key] = value

        else:

            payload[mapping.mqtt_key] = value

    if not payload:
        return {}

    return {group: payload}
