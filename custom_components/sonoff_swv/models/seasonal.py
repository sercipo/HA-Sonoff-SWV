from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SeasonalSettings:
    """Coefficienti stagionali."""

    january: float = 1
    february: float = 1
    march: float = 1
    april: float = 1
    may: float = 1
    june: float = 1
    july: float = 1
    august: float = 1
    september: float = 1
    october: float = 1
    november: float = 1
    december: float = 1

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "SeasonalSettings":

        return cls(**data)

    def to_dict(self) -> dict:

        return {

            "january": self.january,
            "february": self.february,
            "march": self.march,
            "april": self.april,
            "may": self.may,
            "june": self.june,
            "july": self.july,
            "august": self.august,
            "september": self.september,
            "october": self.october,
            "november": self.november,
            "december": self.december,

        }

    def update_from_dict(
        self,
        data: dict,
    ) -> None:

        updated = SeasonalSettings.from_dict(
            data
        )

        self.january = updated.january
        self.february = updated.february
        self.march = updated.march
        self.april = updated.april
        self.may = updated.may
        self.june = updated.june
        self.july = updated.july
        self.august = updated.august
        self.september = updated.september
        self.october = updated.october
        self.november = updated.november
        self.december = updated.december