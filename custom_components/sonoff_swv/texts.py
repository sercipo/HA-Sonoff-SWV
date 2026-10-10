"""Testi dell'integrazione in inglese e italiano (nessuna dipendenza da HA)."""
from __future__ import annotations

DEFAULT_LANGUAGE = "en"

TEXTS = {
    "en": {
        "valve_open": "Irrigation valve open",
        "valve_closed": "Irrigation valve closed",
        "plan_started": "Irrigation started.",
        "plan_started_end": "Irrigation started, expected end at {end}.",
        "plan_ended": "Irrigation finished: {liters} L in {minutes} {unit} ({start}-{end}).",
        "plan_warning": "{plan} starts in {remaining} {unit} ({start}): expected {expected}.",
        "alarm_water_shortage": "Alarm: water shortage.",
        "alarm_water_leak": "Alarm: water leak detected.",
        "minute_one": "minute",
        "minute_other": "minutes",
        "hour_one": "hour",
        "hour_other": "hours",
        "plan_name": "Plan {n}",
        "origin_manual": "Manual",
        "rain_active": "Active",
        "rain_inactive": "Inactive",
        "rain_detail": "Delay of {hours} {unit} set on {date} at {time}",
        "date_format": "%Y-%m-%d",
        "none": "None",
        "telegram": "Telegram",
        "app": "Companion app",
    },
    "it": {
        "valve_open": "Valvola irrigazione aperta",
        "valve_closed": "Valvola irrigazione chiusa",
        "plan_started": "Irrigazione avviata.",
        "plan_started_end": "Irrigazione avviata, fine prevista alle {end}.",
        "plan_ended": "Irrigazione terminata: {liters} L in {minutes} {unit} ({start}-{end}).",
        "plan_warning": "Tra {remaining} {unit} parte l'irrigazione del {plan} ({start}): previsti {expected}.",
        "alarm_water_shortage": "Allarme: manca l'acqua.",
        "alarm_water_leak": "Allarme: rilevata una perdita d'acqua.",
        "minute_one": "minuto",
        "minute_other": "minuti",
        "hour_one": "ora",
        "hour_other": "ore",
        "plan_name": "Piano {n}",
        "origin_manual": "Manuale",
        "rain_active": "Attivo",
        "rain_inactive": "Disattivo",
        "rain_detail": "Ritardo di {hours} {unit} impostato il {date} alle {time}",
        "date_format": "%d-%m-%Y",
        "none": "Nessuno",
        "telegram": "Telegram",
        "app": "App companion",
    },
}


def normalize_language(code) -> str:
    """'it', 'it-IT', 'pt_BR' -> lingua disponibile, altrimenti inglese."""
    base = str(code or "").replace("_", "-").split("-")[0].lower()
    return base if base in TEXTS else DEFAULT_LANGUAGE


def translate(lang: str, key: str, **kwargs) -> str:
    table = TEXTS.get(lang) or TEXTS[DEFAULT_LANGUAGE]
    template = table.get(key) or TEXTS[DEFAULT_LANGUAGE].get(key, key)
    try:
        return template.format(**kwargs)
    except (KeyError, IndexError):
        return template