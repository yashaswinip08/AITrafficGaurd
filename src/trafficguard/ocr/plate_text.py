"""Indian number-plate normalization and validation logic."""

from __future__ import annotations

import re
from dataclasses import dataclass


OCR_LETTER_CORRECTIONS = {'0': 'O', '1': 'I', '2': 'Z', '5': 'S', '6': 'G', '8': 'B'}
OCR_DIGIT_CORRECTIONS = {'O': '0', 'I': '1', 'S': '5', 'Z': '2', 'G': '6', 'B': '8'}


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

    cleaned = re.sub(r"[^A-Za-z0-9]", "", raw_text.upper())
    if cleaned in {"UNKNOWN", "UNKN0WN"}:
        cleaned = "UNKNOWN"
    else:
        cleaned = _correct_ocr_confusions(cleaned)

    valid = _looks_like_indian_plate(cleaned)
    return PlateReading(
        raw_text=raw_text,
        cleaned_text=cleaned,
        confidence=confidence,
        valid_format=valid,
    )


def _looks_like_indian_plate(value: str) -> bool:
    value = value.strip().upper()
    return 8 <= len(value) <= 12 and bool(re.fullmatch(r"[A-Z]{2}\d{1,2}[A-Z]{1,3}\d{1,4}", value))


def _correct_ocr_confusions(value: str) -> str:
    if _looks_like_indian_plate(value):
        return value

    for rto_length in (2, 1):
        for series_length in (2, 1, 3):
            for number_length in (4, 3, 2, 1):
                if len(value) != 2 + rto_length + series_length + number_length:
                    continue

                state_end = 2
                rto_end = state_end + rto_length
                series_end = rto_end + series_length
                state = _convert_characters(value[:state_end], OCR_LETTER_CORRECTIONS)
                rto = _convert_characters(value[state_end:rto_end], OCR_DIGIT_CORRECTIONS)
                series = _convert_characters(value[rto_end:series_end], OCR_LETTER_CORRECTIONS)
                number = _convert_characters(value[series_end:], OCR_DIGIT_CORRECTIONS)
                candidate = state + rto + series + number
                if _looks_like_indian_plate(candidate):
                    return candidate

    return value


def _convert_characters(value: str, corrections: dict[str, str]) -> str:
    return "".join(corrections.get(character, character) for character in value)
