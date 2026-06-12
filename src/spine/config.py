"""Configuration loading for Phase 00 SPINE scaffolds."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib
from typing import Any


@dataclass(frozen=True)
class SpineConfig:
    track: str
    data: dict[str, Any]
    source_path: Path

    def get(self, section: str, key: str) -> Any:
        return self.data[section][key]


def load_config(path: str | Path) -> SpineConfig:
    config_path = Path(path)
    with config_path.open("rb") as handle:
        data = tomllib.load(handle)
    track = str(data.get("meta", {}).get("track", data.get("track", "unknown")))
    return SpineConfig(track=track, data=data, source_path=config_path)
