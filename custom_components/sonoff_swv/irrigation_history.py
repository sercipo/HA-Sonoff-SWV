"""Irrigation history: build, store and summarize per-session irrigation events.

Source data is Device.irrigation_schedule_status, which the device publishes
close to real time during start/running/end transitions (verified empirically
on 27/09/2026). This module only builds/aggregates plain dicts; it has no
dependency on Home Assistant and can be tested standalone.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any


DEFAULT_RETENTION_DAYS = 90

UNIT_TO_LITERS = {
    "liter": 1.0,
    "us_gallon": 3.78541,
    "imperial_gallon": 4.54609,
}


def _to_liters(amount: float | int | None, unit: str | None) -> float | None:
    """Convert a device amount + unit into liters."""

    if amount is None:
        return None

    factor = UNIT_TO_LITERS.get(unit or "liter", 1.0)

    return round(amount * factor, 3)


def _parse_datetime(value: str | None) -> datetime | None:
    """Parse an ISO datetime string, tolerating missing/invalid values."""

    if not value:
        return None

    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def build_event_from_status(
    status: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Build a normalized history event from irrigation_schedule_status.

    Returns None when the status is not a completed ("end") schedule, or
    when it is missing the fields needed to identify the event.
    """

    if not isinstance(status, dict):
        return None

    if status.get("schedule_status") != "end":
        return None

    start_time = status.get("start_time")
    end_time = status.get("actual_end_time")

    if not start_time or not end_time:
        return None

    return {
        "schedule_index": status.get("schedule_index"),
        "type": status.get("schedule_type"),
        "mode": status.get("irrigation_mode"),
        "start_time": start_time,
        "end_time": end_time,
        "amount_liters": _to_liters(
            status.get("actual_irrigation_amount"),
            status.get("irrigation_amount_unit"),
        ),
    }


def upsert_event(
    history: list[dict[str, Any]],
    event: dict[str, Any],
) -> list[dict[str, Any]]:
    """Insert a new event, or update it in place if already present.

    Identity is (start_time, schedule_index): the device may republish the
    same "end" status again with a more accurate amount once the flow
    sensor settles, so a later call for the same event replaces the
    earlier one instead of creating a duplicate.
    """

    for index, existing in enumerate(history):

        if (
            existing.get("start_time") == event.get("start_time")
            and existing.get("schedule_index") == event.get("schedule_index")
        ):

            history[index] = event

            return history

    history.append(event)

    return history


def prune_history(
    history: list[dict[str, Any]],
    days: int = DEFAULT_RETENTION_DAYS,
) -> list[dict[str, Any]]:
    """Drop events older than the retention window."""

    cutoff = datetime.now().astimezone() - timedelta(days=days)

    pruned = []

    for event in history:

        end_time = _parse_datetime(event.get("end_time"))

        if end_time is None:
            continue

        if end_time >= cutoff:
            pruned.append(event)

    return pruned


def summarize_last_event(
    history: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Return the most recent completed irrigation event."""

    valid = [
        event
        for event in history
        if _parse_datetime(event.get("end_time")) is not None
    ]

    if not valid:
        return None

    return max(
        valid,
        key=lambda event: event["end_time"],
    )


def sum_last_days(
    history: list[dict[str, Any]],
    days: int,
) -> float:
    """Sum amount_liters for events ending within the last `days` days."""

    cutoff = datetime.now().astimezone() - timedelta(days=days)

    total = 0.0

    for event in history:

        end_time = _parse_datetime(event.get("end_time"))

        if end_time is None or end_time < cutoff:
            continue

        amount = event.get("amount_liters")

        if amount:
            total += amount

    return round(total, 2)


def daily_series(
    history: list[dict[str, Any]],
    days: int,
) -> dict[str, Any]:
    """Build a per-day series split by manual/automatic, oldest first."""

    today = datetime.now().astimezone().date()

    day_list = [
        today - timedelta(days=offset)
        for offset in range(days - 1, -1, -1)
    ]

    manual = {day: 0.0 for day in day_list}
    automatic = {day: 0.0 for day in day_list}

    for event in history:

        end_time = _parse_datetime(event.get("end_time"))

        if end_time is None:
            continue

        day = end_time.date()

        if day not in manual:
            continue

        amount = event.get("amount_liters") or 0.0

        if event.get("type") == "manual":
            manual[day] += amount
        else:
            automatic[day] += amount

    return {
        "days": [day.isoformat() for day in day_list],
        "manual_liters": [round(manual[day], 2) for day in day_list],
        "automatic_liters": [round(automatic[day], 2) for day in day_list],
    }