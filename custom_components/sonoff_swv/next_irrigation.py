"""Calcolo della prossima irrigazione pianificata (nessuna dipendenza da HA)."""
from __future__ import annotations

from datetime import datetime, time, timedelta

WEEKDAY_KEYS = (
    "monday", "tuesday", "wednesday", "thursday",
    "friday", "saturday", "sunday",
)  # indice = date.weekday()


def _parse_time(value) -> time | None:
    try:
        hh, mm = str(value).split(":")[:2]
        return time(int(hh), int(mm))
    except (ValueError, TypeError):
        return None


def _parse_date(value):
    try:
        return datetime.fromisoformat(str(value)).date()
    except (ValueError, TypeError):
        return None


def next_run(plan: dict, now: datetime) -> datetime | None:
    """Prossimo avvio del piano dopo `now`, oppure None se il piano non è attivo."""
    if not plan or not plan.get("enable_state"):
        return None

    start = _parse_time(plan.get("start_time"))
    if start is None:
        return None

    tz = now.tzinfo
    first_day = _parse_date(plan.get("enable_date")) or now.date()
    mode = plan.get("loop_type_mode")

    if mode == "day_interval":
        try:
            step = max(int(plan.get("loop_type_interval_days") or 1), 1)
        except (ValueError, TypeError):
            step = 1
        anchor = first_day
        created = _parse_date(plan.get("create_datetime"))
        if created is not None and created > anchor:
            anchor = created
        today = now.date()
        k0 = 0 if today <= anchor else (today - anchor).days // step
        for k in range(k0, k0 + 3):
            day = anchor + timedelta(days=k * step)
            candidate = datetime.combine(day, start, tzinfo=tz)
            if candidate > now:
                return candidate
        return None

    if mode == "weekdays":
        days = plan.get("loop_type_week_days") or {}
        if not any(days.get(k) for k in WEEKDAY_KEYS):
            return None
        base = max(now.date(), first_day)
        for i in range(8):
            day = base + timedelta(days=i)
            if days.get(WEEKDAY_KEYS[day.weekday()]):
                candidate = datetime.combine(day, start, tzinfo=tz)
                if candidate > now:
                    return candidate
        return None

    return None


UNIT_LABELS = {
    "liter": "L",
    "us_gallon": "gal US",
    "imperial_gallon": "gal UK",
}


def describe_run(plan: dict, start: datetime) -> dict:
    """Descrizione leggibile: volume se modalità capacity, altrimenti durata."""
    info = {
        "plan_index": plan.get("plan_index"),
        "plan": f"Piano {plan.get('plan_index')}",
        "start_time": start.isoformat(),
        "mode": plan.get("irrigation_mode"),
    }
    if plan.get("irrigation_mode") == "capacity":
        unit = plan.get("irrigation_amount_unit")
        info["amount"] = plan.get("irrigation_amount")
        info["amount_unit"] = unit
        info["expected"] = f"{plan.get('irrigation_amount')} {UNIT_LABELS.get(unit, unit or '')}".strip()
    else:
        minutes = (
            plan.get("irrigation_total_duration")
            or plan.get("irrigation_duration")
        )
        info["duration_minutes"] = minutes
        info["expected"] = f"{minutes} min"
    total = plan.get("irrigation_total_duration")
    if isinstance(total, (int, float)) and total:
        info["expected_end_time"] = (start + timedelta(minutes=total)).isoformat()
    return info


def upcoming_runs(plans: dict, now: datetime) -> list[dict]:
    """Prossimo avvio di ogni piano attivo, ordinato dal più vicino."""
    runs = []
    for plan in plans.values():
        start = next_run(plan, now)
        if start is not None:
            runs.append(describe_run(plan, start))
    runs.sort(key=lambda r: r["start_time"])
    return runs


def next_event(plans: dict, now: datetime) -> dict | None:
    runs = upcoming_runs(plans, now)
    return runs[0] if runs else None