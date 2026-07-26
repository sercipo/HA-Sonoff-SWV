from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Device:
    """Informazioni del dispositivo Zigbee."""

    ieeeAddr: str = ""

    friendlyName: str = ""

    manufacturerName: str = ""

    model: str = ""

    softwareBuildID: str = ""

    hardwareVersion: int = 0

    powerSource: str = ""

    dateCode: str = ""

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "Device":

        device = cls()

        device.ieeeAddr = data.get(
            "ieeeAddr",
            "",
        )

        device.friendlyName = data.get(
            "friendlyName",
            "",
        )

        device.manufacturerName = data.get(
            "manufacturerName",
            "",
        )

        device.model = data.get(
            "model",
            "",
        )

        device.softwareBuildID = data.get(
            "softwareBuildID",
            "",
        )

        device.hardwareVersion = data.get(
            "hardwareVersion",
            0,
        )

        device.powerSource = data.get(
            "powerSource",
            "",
        )

        device.dateCode = data.get(
            "dateCode",
            "",
        )

        return device

    def to_dict(self) -> dict:

        return {
            "ieeeAddr": self.ieeeAddr,
            "friendlyName": self.friendlyName,
            "manufacturerName": self.manufacturerName,
            "model": self.model,
            "softwareBuildID": self.softwareBuildID,
            "hardwareVersion": self.hardwareVersion,
            "powerSource": self.powerSource,
            "dateCode": self.dateCode,
        }