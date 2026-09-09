#!/usr/bin/env python3
"""Read battery information from OpenRazer's mouse driver without changing settings."""

import json
from pathlib import Path
from typing import TypedDict


class Battery(TypedDict):
    name: str
    percentage: int
    charging: bool


class Status(TypedDict):
    devices: list[Battery]
    error: str


def read_batteries(root: Path = Path("/sys/bus/hid/drivers/razermouse")) -> Status:
    if not root.is_dir():
        return {"devices": [], "error": "OpenRazer mouse driver is not loaded."}

    devices: dict[str, Battery] = {}
    errors: list[str] = []
    for path in sorted(root.glob("0003:1532:*")):
        if not (path / "charge_level").exists():
            continue
        try:
            # An idle receiver returns zero charge and an empty serial when
            # its mouse is off or connected through the charging cable.
            serial = (path / "device_serial").read_text().strip("\0\n ")
            if not serial:
                continue
            name = (path / "device_type").read_text().strip()
            level = int((path / "charge_level").read_text())
            charging = int((path / "charge_status").read_text())
            if not name or not 0 <= level <= 255 or charging not in (0, 1):
                raise ValueError("Invalid battery response")
            battery: Battery = {
                "name": name,
                "percentage": round(level * 100 / 255),
                "charging": bool(charging),
            }
            # Prefer the charging connection if both USB paths answer.
            if serial not in devices or battery["charging"]:
                devices[serial] = battery
        except FileNotFoundError:
            continue  # A mouse can disconnect between attribute reads.
        except (OSError, ValueError) as error:
            errors.append(f"{path.name}: {error}")

    return {
        "devices": sorted(devices.values(), key=lambda device: device["name"]),
        "error": "\n".join(errors),
    }


if __name__ == "__main__":
    print(json.dumps(read_batteries()))
