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

def _duration_text(plan: dict) -> str:
    """Testo della durata: totale, con ciclo e pausa se la modalità li usa."""
    total = plan.get("irrigation_total_duration") or plan.get("irrigation_duration")
    text = f"{total} min"
    if plan.get("irrigation_mode") == "duration_with_interval":
        cycle = plan.get("irrigation_duration")
        pause = plan.get("interval_duration")
        if cycle and pause:
            text += f" (cicli da {cycle} min, pausa {pause} min)"
    return text

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
        info["expected"] = _duration_text(plan)
        if plan.get("irrigation_mode") == "duration_with_interval":
            info["cycle_minutes"] = plan.get("irrigation_duration")
            info["pause_minutes"] = plan.get("interval_duration")
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

DAYS_IT = ("lun", "mar", "mer", "gio", "ven", "sab", "dom")


def format_plan_line(plan: dict | None, now: datetime) -> str:
    """Riga di testo leggibile per la card."""
    if not plan:
        return "non noto"

    state = "ATTIVO" if plan.get("enable_state") else "disattivo"
    start = plan.get("start_time") or "--:--"

    if plan.get("loop_type_mode") == "weekdays":
        days = plan.get("loop_type_week_days") or {}
        cadence = ",".join(
            DAYS_IT[i] for i, k in enumerate(WEEKDAY_KEYS) if days.get(k)
        ) or "nessun giorno"
    else:
        cadence = f"ogni {plan.get('loop_type_interval_days') or 1} gg"

    if plan.get("irrigation_mode") == "capacity":
        unit = plan.get("irrigation_amount_unit")
        qty = f"{plan.get('irrigation_amount')} {UNIT_LABELS.get(unit, unit or '')}".strip()
    else:
        qty = _duration_text(plan)

    line = f"{state} | {start} | {cadence} | {qty}"

    nxt = next_run(plan, now)
    if nxt is not None:
        line += f" | prossima {nxt.strftime('%d/%m %H:%M')}"

    return line

def _parse_dt(value):
    try:
        return datetime.fromisoformat(str(value))
    except (ValueError, TypeError):
        return None


def check_sync(plans: dict, status, now: datetime, ignored=None) -> list[str]:
    """Avvisi se la prossima irrigazione del device non coincide con la nostra.

    Solo un indizio: il device non è interrogabile sui piani.
    """
    if not isinstance(status, dict) or status.get("schedule_status") != "standby":
        return []

    dev_start = _parse_dt(status.get("start_time"))
    if dev_start is None or dev_start.tzinfo is None or dev_start <= now:
        return []

    signature = {
        "schedule_index": status.get("schedule_index"),
        "start_time": status.get("start_time"),
    }
    if ignored and ignored == signature:
        return []

    dev_txt = f"{dev_start.strftime('%d/%m %H:%M')} (piano {status.get('schedule_index')})"

    ours = next_event(plans, now)
    if ours is None:
        return [f"Piani non allineati: il device prevede {dev_txt}, l'integrazione non ha piani attivi"]

    our_start = _parse_dt(ours["start_time"])
    if abs((dev_start - our_start).total_seconds()) > 60:
        return [
            f"Piani non allineati: device {dev_txt}, "
            f"integrazione {our_start.strftime('%d/%m %H:%M')} (piano {ours['plan_index']})"
        ]

    return []