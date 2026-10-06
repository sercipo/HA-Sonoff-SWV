"""Archivio dei piani di irrigazione (nessuna dipendenza da Home Assistant)."""
from __future__ import annotations

from datetime import datetime

PLAN_FIELDS = (
    "plan_index",
    "enable_state",
    "loop_type_mode",
    "loop_type_interval_days",
    "loop_type_week_days",
    "enable_date",
    "start_time",
    "irrigation_mode",
    "irrigation_total_duration",
    "irrigation_duration",
    "interval_duration",
    "irrigation_amount",
    "irrigation_amount_unit",
    "fail_safe",
    "create_datetime",
)


def normalize_plan(data: dict, source: str, now: datetime) -> dict | None:
    """Estrae i campi del piano da un report o dal form. None se manca plan_index."""
    if not isinstance(data, dict) or data.get("plan_index") is None:
        return None
    plan = {k: data.get(k) for k in PLAN_FIELDS}
    week = data.get("loop_type_week_days")
    plan["loop_type_week_days"] = dict(week) if isinstance(week, dict) else {}
    plan["source"] = source  # "report" | "ha_write"
    plan["updated_at"] = now.isoformat()
    return plan


def upsert_plan(plans: dict, plan: dict) -> dict:
    """Chiave = indice come stringa (JSON). Un campo None non cancella un valore già noto."""
    key = str(plan["plan_index"])
    old = plans.get(key, {})
    merged = dict(plan)
    for field in PLAN_FIELDS:
        if merged.get(field) is None and old.get(field) is not None:
            merged[field] = old[field]
    plans[key] = merged
    return plans


def remove_plan(plans: dict, plan_index: int) -> dict:
    plans.pop(str(plan_index), None)
    return plans


def plans_overview(plans: dict, indexes) -> dict:
    """Piani attivi / inattivi / mai visti (sconosciuti)."""
    active, inactive, unknown = [], [], []
    for i in indexes:
        plan = plans.get(str(i))
        if plan is None:
            unknown.append(i)
        elif plan.get("enable_state"):
            active.append(i)
        else:
            inactive.append(i)
    return {"active": active, "inactive": inactive, "unknown": unknown}
    
WEEKDAYS = (
    "monday", "tuesday", "wednesday", "thursday",
    "friday", "saturday", "sunday",
)

# Valori iniziali del form per un piano non ancora noto.
# enable_state resta False: un piano nuovo non si attiva da solo.
# enable_date e create_datetime vuoti: li compila il bottone al salvataggio.
PLAN_DEFAULTS = {
    "enable_state": False,
    "loop_type_mode": "day_interval",
    "loop_type_interval_days": 1,
    "loop_type_week_days": {day: False for day in WEEKDAYS},
    "enable_date": None,
    "start_time": "06:00",
    "irrigation_mode": "capacity",
    "irrigation_total_duration": 1,
    "irrigation_duration": 1,
    "interval_duration": 1,
    "irrigation_amount": 1,
    "irrigation_amount_unit": "liter",
    "fail_safe": 10,
    "create_datetime": None,
}

# campo del piano -> attributo del Device (i campi del form)
FORM_FIELD_MAP = {
    "enable_state": "irrigation_plan_enabled",
    "loop_type_mode": "irrigation_plan_loop_type",
    "loop_type_interval_days": "irrigation_plan_interval_days",
    "enable_date": "irrigation_plan_enable_date",
    "start_time": "irrigation_plan_start_time",
    "irrigation_mode": "irrigation_plan_mode",
    "irrigation_total_duration": "irrigation_plan_total_duration",
    "irrigation_duration": "irrigation_plan_duration",
    "interval_duration": "irrigation_plan_interval_duration",
    "irrigation_amount": "irrigation_plan_amount",
    "irrigation_amount_unit": "irrigation_plan_amount_unit",
    "fail_safe": "irrigation_plan_fail_safe",
    "create_datetime": "irrigation_plan_create_datetime",
}


def plan_from_form(get, plan_index) -> dict:
    """Costruisce un piano dai campi del form. get(attr) legge dal Device."""
    raw = {field: get(attr) for field, attr in FORM_FIELD_MAP.items()}
    raw["plan_index"] = plan_index
    raw["loop_type_week_days"] = {
        day: bool(get(f"irrigation_plan_{day}")) for day in WEEKDAYS
    }
    return raw


def form_values_from_plan(plan: dict) -> dict:
    """Valori da assegnare agli attributi del Device per popolare il form."""
    values = {attr: plan.get(field) for field, attr in FORM_FIELD_MAP.items()}
    week = plan.get("loop_type_week_days") or {}
    for day in WEEKDAYS:
        values[f"irrigation_plan_{day}"] = bool(week.get(day, False))
    return values