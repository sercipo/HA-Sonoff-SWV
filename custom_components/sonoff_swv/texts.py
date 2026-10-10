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
        "short_datetime_format": "%d %b %H:%M",
        "none": "None",
        "telegram": "Telegram",
        "app": "Companion app",
        "weekdays_short": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "plan_unknown": "unknown",
        "plan_state_active": "ACTIVE",
        "plan_state_inactive": "inactive",
        "plan_no_days": "no days",
        "plan_every_days": "every {n} d",
        "plan_next": "next {when}",
        "cycles_text": " (cycles of {cycle} min, pause {pause} min)",
        "warnings_none": "none",
        "sync_dev": "{when} (plan {n})",
        "sync_no_plans": "Plans not aligned: the device expects {dev}, the integration has no active plans",
        "sync_mismatch": "Plans not aligned: device {dev}, integration {ours} (plan {n})",
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
        "short_datetime_format": "%d/%m %H:%M",
        "none": "Nessuno",
        "telegram": "Telegram",
        "app": "App companion",
        "weekdays_short": "lun,mar,mer,gio,ven,sab,dom",
        "plan_unknown": "non noto",
        "plan_state_active": "ATTIVO",
        "plan_state_inactive": "disattivo",
        "plan_no_days": "nessun giorno",
        "plan_every_days": "ogni {n} gg",
        "plan_next": "prossima {when}",
        "cycles_text": " (cicli da {cycle} min, pausa {pause} min)",
        "warnings_none": "nessuno",
        "sync_dev": "{when} (piano {n})",
        "sync_no_plans": "Piani non allineati: il device prevede {dev}, l'integrazione non ha piani attivi",
        "sync_mismatch": "Piani non allineati: device {dev}, integrazione {ours} (piano {n})",
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