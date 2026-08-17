from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er


# Maps the internal Sonoff SWV Device key to the MQTT/Zigbee2MQTT key.
#
# MQTT unique_id format:
#
#   <ieee>_<mqtt_key>_zigbee2mqtt
#
MQTT_KEY_MAP: dict[str, str] = {
    # Basic
    "battery": "battery",
    "state": "switch",
    "linkquality": "linkquality",

    # Irrigation plan
    "irrigation_plan_mode": "irrigation_plan_mode",
    "irrigation_plan_amount": "irrigation_plan_amount",
    "irrigation_plan_duration": "irrigation_plan_duration",
    "irrigation_plan_total_duration": "irrigation_plan_total_duration",
    "irrigation_plan_interval_duration": "irrigation_plan_interval_duration",
    "irrigation_plan_interval_days": "irrigation_plan_interval_days",
    "irrigation_plan_fail_safe": "irrigation_plan_fail_safe",
    "irrigation_plan_enabled": "switch_irrigation_plan_enabled",
    "irrigation_plan_loop_type": "irrigation_plan_loop_type",
    "irrigation_plan_start_time": "irrigation_plan_start_time",

    # Weekdays
    "irrigation_plan_monday": "switch_irrigation_plan_monday",
    "irrigation_plan_tuesday": "switch_irrigation_plan_tuesday",
    "irrigation_plan_wednesday": "switch_irrigation_plan_wednesday",
    "irrigation_plan_thursday": "switch_irrigation_plan_thursday",
    "irrigation_plan_friday": "switch_irrigation_plan_friday",
    "irrigation_plan_saturday": "switch_irrigation_plan_saturday",
    "irrigation_plan_sunday": "switch_irrigation_plan_sunday",

    # Manual irrigation
    "manual_irrigation_amount": "manual_irrigation_amount",
    "manual_irrigation_duration": "manual_irrigation_duration",
    "manual_irrigation_total_duration": "manual_irrigation_total_duration",
    "manual_interval_duration": "manual_interval_duration",
    "manual_fail_safe": "manual_fail_safe",
    "manual_irrigation_mode": "manual_irrigation_mode",

    # Alarms
    "enable_alarm_water_shortage": "switch_enable_alarm_water_shortage",
    "enable_alarm_water_leak": "switch_enable_alarm_water_leak",
    "enable_water_shortage_auto_close": "switch_enable_water_shortage_auto_close",
    "enable_water_leak_auto_close": "switch_enable_water_leak_auto_close",

    # Irrigation status / history
    "irrigation_schedule_status": "irrigation_schedule_status",
    "irrigation_plan_report": "irrigation_plan_report",
    "real_time_irrigation_volume": "real_time_irrigation_volume",
    "real_time_irrigation_duration": "real_time_irrigation_duration",
    "daily_irrigation_volume": "daily_irrigation_volume",
    "daily_irrigation_duration": "daily_irrigation_duration",
    "hour_irrigation_volume": "hour_irrigation_volume",
    "hour_irrigation_duration": "hour_irrigation_duration",

    # Valve
    "valve_abnormal_state": "valve_abnormal_state",

    # Rain delay
    "rain_delay": "rain_delay",
    "rain_delay_end_datetime": "rain_delay_end_datetime",

    # Seasonal adjustment
    "seasonal_january": "seasonal_watering_adjustment_january",
    "seasonal_february": "seasonal_watering_adjustment_february",
    "seasonal_march": "seasonal_watering_adjustment_march",
    "seasonal_april": "seasonal_watering_adjustment_april",
    "seasonal_may": "seasonal_watering_adjustment_may",
    "seasonal_june": "seasonal_watering_adjustment_june",
    "seasonal_july": "seasonal_watering_adjustment_july",
    "seasonal_august": "seasonal_watering_adjustment_august",
    "seasonal_september": "seasonal_watering_adjustment_september",
    "seasonal_october": "seasonal_watering_adjustment_october",
    "seasonal_november": "seasonal_watering_adjustment_november",
    "seasonal_december": "seasonal_watering_adjustment_december",

    # Child lock
    "child_lock": "switch_child_lock",
}


def build_mqtt_unique_id(
    ieee: str,
    key: str,
) -> str:
    """Build the Zigbee2MQTT entity unique_id."""

    mqtt_key = MQTT_KEY_MAP.get(key, key)

    return f"{ieee}_{mqtt_key}_zigbee2mqtt"


def _normalize_ieee(
    ieee: str,
) -> str:
    """Normalize an IEEE address for comparison."""

    return ieee.lower().replace("0x", "")


def find_mqtt_entity(
    hass: HomeAssistant,
    ieee: str | None,
    key: str,
) -> str | None:
    """Find an existing MQTT entity by stable unique_id."""

    registry = er.async_get(hass)

    mqtt_key = MQTT_KEY_MAP.get(key, key)

    if not mqtt_key:
        return None

    # First try the exact expected unique_id.
    if ieee:
        normalized_ieee = _normalize_ieee(ieee)

        for ieee_value in (
            ieee,
            f"0x{normalized_ieee}",
            normalized_ieee,
        ):
            unique_id = build_mqtt_unique_id(
                ieee_value,
                key,
            )

            for domain in (
                "sensor",
                "binary_sensor",
                "number",
                "switch",
                "select",
                "button",
                "time",
                "datetime",
                "text",
                "update",
            ):
                entity_id = registry.async_get_entity_id(
                    domain,
                    "mqtt",
                    unique_id,
                )

                if entity_id is not None:
                    return entity_id

    # Fallback:
    #
    # If the device IEEE representation used internally by the
    # integration differs from the representation used by MQTT,
    # search by the stable MQTT suffix.
    #
    # This does NOT depend on the entity_id/name, so renaming an
    # MQTT entity does not break the resolver.
    suffix = f"_{mqtt_key}_zigbee2mqtt"

    matches: list[str] = []

    for entity_entry in registry.entities.values():
        if entity_entry.platform != "mqtt":
            continue

        unique_id = entity_entry.unique_id

        if not unique_id:
            continue

        if unique_id.endswith(suffix):
            matches.append(entity_entry.entity_id)

    # Only use the fallback when there is exactly one match.
    # This prevents accidentally binding to another device if
    # multiple identical SWV devices are installed.
    if len(matches) == 1:
        return matches[0]

    return None


def mqtt_entity_exists(
    hass: HomeAssistant,
    ieee: str | None,
    mqtt_key: str,
) -> bool:
    """Return True if an MQTT entity exists."""

    return find_mqtt_entity(
        hass,
        ieee,
        mqtt_key,
    ) is not None