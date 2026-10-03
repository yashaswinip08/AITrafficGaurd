"""Indian number-plate normalization and validation logic."""

from __future__ import annotations

import re
from dataclasses import dataclass


CONFUSION_MAP = {
    'O': '0',
    'o': '0',
    'I': '1',
    'i': '1',
    'S': '5',
    's': '5',
    'Z': '2',
    'z': '2',
    'G': '6',
    'g': '6',
}


@dataclass
class PlateReading:
    raw_text: str
    cleaned_text: str
    confidence: float
    valid_format: bool


def normalize_plate_text(raw_text: str, confidence: float = 0.0) -> PlateReading:
    """Clean OCR plate output into a standardized Indian plate-like string."""
    if raw_text is None:
        raw_text = ""

    stripped = raw_text.strip()
    cleaned = re.sub(r"[^A-Za-z0-9]", "", stripped.upper())
    for source, target in CONFUSION_MAP.items():
        cleaned = cleaned.replace(source, target)

    # Prefer common Indian plate structure: state code + numeric + alpha + numeric
    cleaned = cleaned.replace(" ", "")
    cleaned = cleaned.replace("-", "")
    cleaned = cleaned.replace(".", "")
    cleaned = cleaned.replace("_", "")

    valid = _looks_like_indian_plate(cleaned)
    return PlateReading(
        raw_text=raw_text,
        cleaned_text=cleaned,
        confidence=confidence,
        valid_format=valid,
    )


def _looks_like_indian_plate(value: str) -> bool:
    value = value.strip().upper()
    if len(value) < 8 or len(value) > 12:
        return False

    if not value[:2].isalpha():
        return False
    if not value[2:4].isdigit():
        return False

    if len(value) >= 10:
        return value[4:6].isalpha() and value[6:].isdigit() and len(value[6:]) >= 4

    return any(ch.isalpha() for ch in value[4:]) and any(ch.isdigit() for ch in value[4:])
