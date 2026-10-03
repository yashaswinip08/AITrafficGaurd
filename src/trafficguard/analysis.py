"""Helpers for OCR-backed vehicle analysis and violation summaries."""

from __future__ import annotations

import io
import logging
import threading
from typing import Any, Iterable

import numpy as np
from PIL import Image

from .ocr.ocr_engine import OcrEngine
from .ocr.plate_text import PlateReading, normalize_plate_text

logger = logging.getLogger(__name__)
_vehicle_detector: Any | None = None
_vehicle_detector_lock = threading.Lock()

VEHICLE_WHEEL_CATEGORIES = {
    "bicycle": "2-wheeler",
    "motorcycle": "2-wheeler",
    "car": "4-wheeler",
    "bus": "6+ wheels (estimated)",
    "truck": "6+ wheels (estimated)",
}


def classify_vehicle_detections(detections: Iterable[Any]) -> dict[str, Any]:
    """Map supported object detections to a wheel category using the top confidence."""
    matches: list[tuple[str, str, float]] = []
    for detection in detections:
        if isinstance(detection, dict):
            class_name = str(detection.get("class_name", "")).lower()
            confidence = float(detection.get("confidence", 0.0) or 0.0)
        else:
            class_name = str(getattr(detection, "class_name", "")).lower()
            confidence = float(getattr(detection, "confidence", 0.0) or 0.0)

        wheel_category = VEHICLE_WHEEL_CATEGORIES.get(class_name)
        if wheel_category:
            matches.append((class_name, wheel_category, confidence))

    if not matches:
        return {
            "vehicle_class": "unknown",
            "wheel_category": "unclassified",
            "vehicle_confidence": 0,
        }

    class_name, wheel_category, confidence = max(matches, key=lambda item: item[2])
    return {
        "vehicle_class": class_name,
        "wheel_category": wheel_category,
        "vehicle_confidence": int(round(confidence * 100)),
    }


def _classify_vehicle_image(image: np.ndarray, detector: Any | None = None) -> dict[str, Any]:
    try:
        if detector is None:
            detector = _get_vehicle_detector()
        return classify_vehicle_detections(detector.detect(image))
    except Exception as exc:
        logger.warning("Vehicle classification unavailable: %s", exc)
        return {
            "vehicle_class": "unavailable",
            "wheel_category": "unavailable",
            "vehicle_confidence": 0,
        }


def _get_vehicle_detector() -> Any:
    global _vehicle_detector
    if _vehicle_detector is None:
        with _vehicle_detector_lock:
            if _vehicle_detector is None:
                from .detection.vehicle_detector import VehicleDetector

                _vehicle_detector = VehicleDetector(device="cpu")
    return _vehicle_detector


def pick_best_plate(raw_candidates: Iterable[str | dict[str, Any]]) -> PlateReading:
    """Choose the strongest valid Indian plate read from OCR candidate strings."""
    readings: list[PlateReading] = []
    segments: list[tuple[str, float, tuple[int, int, int, int]]] = []
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
        if isinstance(candidate, dict):
            box = candidate.get("bounding_box")
            if isinstance(box, (list, tuple)) and len(box) == 4:
                segments.append((raw_text, confidence, tuple(map(int, box))))

    for line in _group_ocr_segments(segments):
        for start_index in range(len(line)):
            for end_index in range(start_index + 2, min(start_index + 5, len(line) + 1)):
                joined_text = "".join(segment[0] for segment in line[start_index:end_index])
                joined_confidence = sum(segment[1] for segment in line[start_index:end_index]) / (end_index - start_index)
                readings.append(normalize_plate_text(joined_text, confidence=joined_confidence))

    valid = [reading for reading in readings if reading.valid_format]
    if valid:
        return max(valid, key=lambda item: (item.confidence, len(item.cleaned_text)))

    if readings:
        return max(readings, key=lambda item: (len(item.cleaned_text), item.confidence))

    return normalize_plate_text("UNKNOWN", confidence=0.0)


def _group_ocr_segments(
    segments: list[tuple[str, float, tuple[int, int, int, int]]],
) -> list[list[tuple[str, float, tuple[int, int, int, int]]]]:
    lines: list[list[tuple[str, float, tuple[int, int, int, int]]]] = []
    for segment in sorted(segments, key=lambda item: (item[2][1], item[2][0])):
        x1, y1, x2, y2 = segment[2]
        center_y = (y1 + y2) / 2
        height = max(1, y2 - y1)
        matching_line = next(
            (
                line
                for line in lines
                if abs(center_y - sum((item[2][1] + item[2][3]) / 2 for item in line) / len(line))
                <= max(height, max(item[2][3] - item[2][1] for item in line) * 0.75)
            ),
            None,
        )
        if matching_line is None:
            lines.append([segment])
        else:
            previous = max(matching_line, key=lambda item: item[2][0])
            horizontal_gap = x1 - previous[2][2]
            if horizontal_gap <= max(80, height * 6):
                matching_line.append(segment)
            else:
                lines.append([segment])

    return [sorted(line, key=lambda item: item[2][0]) for line in lines]


def analyze_vehicle_input(
    vehicle_input: Any,
    violation_type: str | None = None,
    *,
    context: str | None = None,
    plate_hint: str | None = None,
    vehicle_detector: Any | None = None,
) -> dict[str, Any]:
    """Turn an uploaded image or raw text into a structured violation analysis."""
    raw_candidates: list[str | dict[str, Any]] = []
    vehicle_analysis = {
        "vehicle_class": "unknown",
        "wheel_category": "unclassified",
        "vehicle_confidence": 0,
    }

    if isinstance(vehicle_input, str):
        raw_candidates = [vehicle_input]
    elif isinstance(vehicle_input, bytes):
        try:
            image = Image.open(io.BytesIO(vehicle_input)).convert("RGB")
            image_array = np.asarray(image)
        except Exception:
            image_array = None
        if image_array is not None:
            try:
                ocr_results = OcrEngine().read_text(image_array)
                raw_candidates = [
                    {"text": item.text, "confidence": item.confidence, "bounding_box": item.bounding_box}
                    for item in ocr_results
                ]
            except Exception:
                raw_candidates = []
            vehicle_analysis = _classify_vehicle_image(image_array, vehicle_detector)
    elif hasattr(vehicle_input, "read"):
        try:
            payload = vehicle_input.read()
            if isinstance(payload, bytes):
                return analyze_vehicle_input(
                    payload,
                    violation_type=violation_type,
                    context=context,
                    plate_hint=plate_hint,
                    vehicle_detector=vehicle_detector,
                )
        except Exception:
            pass
    elif vehicle_input is not None:
        try:
            image_array = np.asarray(vehicle_input)
        except Exception:
            image_array = None
        if image_array is not None:
            try:
                ocr_results = OcrEngine().read_text(image_array)
                raw_candidates = [
                    {"text": item.text, "confidence": item.confidence, "bounding_box": item.bounding_box}
                    for item in ocr_results
                ]
            except Exception:
                raw_candidates = []
            vehicle_analysis = _classify_vehicle_image(image_array, vehicle_detector)

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

    confidence = int(round(best.confidence * 100))
    confidence = max(0, min(100, confidence))

    if vehicle_analysis["vehicle_class"] == "unavailable":
        vehicle_summary = "Vehicle type could not be classified because the detector is unavailable."
    elif vehicle_analysis["vehicle_class"] == "unknown":
        vehicle_summary = "No supported vehicle type was confidently detected in the image."
    else:
        vehicle_summary = (
            f"Detected {vehicle_analysis['wheel_category']} ({vehicle_analysis['vehicle_class']}) "
            f"with {vehicle_analysis['vehicle_confidence']}% model confidence."
        )

    if best.valid_format:
        plate_summary = f"OCR read plate {best.cleaned_text} with {confidence}% confidence."
    else:
        plate_summary = "The registration plate could not be read confidently from this image."

    violation_name = violation_label.replace("_", " ")
    ai_analysis = (
        f"{vehicle_summary} {plate_summary} "
        f"The selected review category is {violation_name}; a single still image cannot confirm this violation. "
        "Verify it against the relevant traffic-signal state or rider-safety evidence."
    )

    recommendation = (
        "Manually verify the plate and compare the event with contextual footage before recording an enforcement action."
        if not best.valid_format
        else "Review the OCR text and contextual footage before recording an enforcement action."
    )

    return {
        "status": "ready" if best.valid_format else "review_needed",
        "violation_type": violation_label,
        "plate": best.cleaned_text if best.valid_format else "UNKNOWN",
        "confidence": confidence,
        "valid_plate_format": best.valid_format,
        "reason": ai_analysis,
        "ai_analysis": ai_analysis,
        "violation_assessment": "requires_context_review",
        "ocr_text": best.raw_text,
        "recommendation": recommendation,
        **vehicle_analysis,
    }
