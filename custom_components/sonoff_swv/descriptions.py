from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NumberDescription:

    object_name: str

    key: str

    name: str

    min_value: float

    max_value: float

    step: float

    unit: str | None = None


@dataclass(frozen=True, slots=True)
class TimeDescription:

    object_name: str

    key: str

    name: str


@dataclass(frozen=True, slots=True)
class SwitchDescription:

    object_name: str

    key: str

    name: str