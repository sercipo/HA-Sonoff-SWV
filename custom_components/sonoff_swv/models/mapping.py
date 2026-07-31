from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Mapping:
    """Mapping between Device attributes and Zigbee2MQTT payload fields."""

    attribute: str
    mqtt_key: str
    group: str | None = None


MAPPINGS: tuple[Mapping, ...] = (

    # Manual irrigation settings

    Mapping(
        attribute="manual_irrigation_amount",
        mqtt_key="irrigation_amount",
        group="manual_default_settings",
    ),

    Mapping(
        attribute="manual_irrigation_amount_unit",
        mqtt_key="irrigation_amount_unit",
        group="manual_default_settings",
    ),

    Mapping(
        attribute="manual_irrigation_mode",
        mqtt_key="irrigation_mode",
        group="manual_default_settings",
    ),

    Mapping(
        attribute="manual_irrigation_duration",
        mqtt_key="irrigation_duration",
        group="manual_default_settings",
    ),

    Mapping(
        attribute="manual_irrigation_total_duration",
        mqtt_key="irrigation_total_duration",
        group="manual_default_settings",
    ),

    Mapping(
        attribute="manual_interval_duration",
        mqtt_key="interval_duration",
        group="manual_default_settings",
    ),

    Mapping(
        attribute="manual_fail_safe",
        mqtt_key="fail_safe",
        group="manual_default_settings",
    ),


    # Irrigation plan settings

    Mapping(
        attribute="irrigation_plan_amount",
        mqtt_key="irrigation_amount",
        group="irrigation_plan_settings",
    ),
    

    Mapping(
        attribute="irrigation_plan_amount_unit",
        mqtt_key="irrigation_amount_unit",
        group="irrigation_plan_settings",
    ),

    Mapping(
        attribute="irrigation_plan_mode",
        mqtt_key="irrigation_mode",
        group="irrigation_plan_settings",
    ),

    Mapping(
        attribute="irrigation_plan_duration",
        mqtt_key="irrigation_duration",
        group="irrigation_plan_settings",
    ),

    Mapping(
        attribute="irrigation_plan_total_duration",
        mqtt_key="irrigation_total_duration",
        group="irrigation_plan_settings",
    ),

    Mapping(
        attribute="irrigation_plan_interval_duration",
        mqtt_key="interval_duration",
        group="irrigation_plan_settings",
    ),

    Mapping(
        attribute="irrigation_plan_fail_safe",
        mqtt_key="fail_safe",
        group="irrigation_plan_settings",
    ),

    Mapping(
        attribute="irrigation_plan_interval_days",
        mqtt_key="loop_type_interval_days",
        group="irrigation_plan_settings",
    ),

    Mapping(
        attribute="irrigation_plan_start_time",
        mqtt_key="start_time",
        group="irrigation_plan_settings",
    ),


    # Simple properties

    Mapping(
        attribute="child_lock",
        mqtt_key="child_lock",
    ),

    Mapping(
        attribute="rain_delay",
        mqtt_key="rain_delay",
    ),

    Mapping(
        attribute="irrigation_plan_enabled",
        mqtt_key="irrigation_plan_enabled",
    ),


    # Alarm settings

    Mapping(
        attribute="enable_alarm_water_shortage",
        mqtt_key="enable_alarm_water_shortage",
        group="valve_alarm_settings",
    ),

    Mapping(
        attribute="enable_alarm_water_leak",
        mqtt_key="enable_alarm_water_leak",
        group="valve_alarm_settings",
    ),

    Mapping(
        attribute="enable_water_shortage_auto_close",
        mqtt_key="enable_water_shortage_auto_close",
        group="valve_alarm_settings",
    ),
)