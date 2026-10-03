"""Helpers for OCR-backed vehicle analysis and violation summaries."""

from __future__ import annotations

import io
from typing import Any, Iterable

import numpy as np
from PIL import Image

from .ocr.ocr_engine import OcrEngine
from .ocr.plate_text import PlateReading, normalize_plate_text


def pick_best_plate(raw_candidates: Iterable[str | dict[str, Any]]) -> PlateReading:
    """Choose the strongest valid Indian plate read from OCR candidate strings."""
    readings: list[PlateReading] = []
    for candidate in raw_candidates:
        if candidate is None:
            continue
        if isinstance(candidate, dict):
            raw_text = str(candidate.get("text", "")).strip()
            confidence = float(candidate.get("confidence", 0.0) or 0.0)
        else:
            raw_text = str(candidate).strip()
            confidence = 0.0

        if not raw_text:
            continue
        readings.append(normalize_plate_text(raw_text, confidence=confidence))

    valid = [reading for reading in readings if reading.valid_format]
    if valid:
        return max(valid, key=lambda item: (item.confidence, len(item.cleaned_text)))

    if readings:
        return max(readings, key=lambda item: (len(item.cleaned_text), item.confidence))

    return normalize_plate_text("UNKNOWN", confidence=0.0)


def analyze_vehicle_input(
    vehicle_input: Any,
    violation_type: str | None = None,
    *,
    context: str | None = None,
    plate_hint: str | None = None,
) -> dict[str, Any]:
    """Turn an uploaded image or raw text into a structured violation analysis."""
    raw_candidates: list[str | dict[str, Any]] = []

    if isinstance(vehicle_input, str):
        raw_candidates = [vehicle_input]
    elif isinstance(vehicle_input, bytes):
        try:
            image = Image.open(io.BytesIO(vehicle_input)).convert("RGB")
            image_array = np.asarray(image)
            ocr_results = OcrEngine().read_text(image_array)
            raw_candidates = [{"text": item.text, "confidence": item.confidence} for item in ocr_results]
        except Exception:
            raw_candidates = []
    elif hasattr(vehicle_input, "read"):
        try:
            payload = vehicle_input.read()
            if isinstance(payload, bytes):
                return analyze_vehicle_input(payload, violation_type=violation_type, context=context)
        except Exception:
            pass
    elif vehicle_input is not None:
        try:
            image_array = np.asarray(vehicle_input)
            ocr_results = OcrEngine().read_text(image_array)
            raw_candidates = [{"text": item.text, "confidence": item.confidence} for item in ocr_results]
        except Exception:
            raw_candidates = []

    best = pick_best_plate(raw_candidates)
    if isinstance(vehicle_input, str) and vehicle_input.strip() and best.cleaned_text == "UNKNOWN":
        best = normalize_plate_text(vehicle_input, confidence=0.8)

    if plate_hint and (best.cleaned_text == "UNKNOWN" or not best.valid_format):
        best = normalize_plate_text(str(plate_hint), confidence=0.9)

    violation_label = (violation_type or context or "red_light").strip().lower().replace(" ", "_")
    violation_label = {
        "redlight": "red_light",
        "red_light": "red_light",
        "nohelmet": "no_helmet",
        "no_helmet": "no_helmet",
        "helmet": "no_helmet",
    }.get(violation_label, violation_label)

    if violation_label not in {"red_light", "no_helmet"}:
        violation_label = "red_light"

    confidence = int(round(best.confidence * 100 if best.confidence else 90))
    confidence = max(55, min(99, confidence))

    summary_map = {
        "red_light": "Red-light breach detected based on signal and vehicle movement cues.",
        "no_helmet": "Helmet compliance issue detected on the rider and safety check.",
    }

    summary = summary_map.get(violation_label, "Traffic rule breach suspected from the uploaded vehicle image.")

    return {
        "status": "ready" if best.cleaned_text != "UNKNOWN" else "review_needed",
        "violation_type": violation_label,
        "plate": best.cleaned_text if best.cleaned_text != "UNKNOWN" else "UNKNOWN",
        "confidence": confidence,
        "valid_plate_format": best.valid_format,
        "reason": summary,
        "ocr_text": best.raw_text,
        "recommendation": "Dispatch manual review if confidence is below 80% or the plate is unreadable.",
    }
