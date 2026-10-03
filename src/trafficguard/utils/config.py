"""Configuration helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: str | Path) -> dict[str, Any]:
    """Load a YAML configuration file."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Config file not found: {file_path}")
    with file_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping: {file_path}")
    return data


def ensure_required_keys(data: dict[str, Any], required: list[str]) -> None:
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError(f"Missing required config keys: {', '.join(missing)}")
