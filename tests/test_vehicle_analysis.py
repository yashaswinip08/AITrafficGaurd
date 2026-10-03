import io
import sys
from types import SimpleNamespace

import numpy as np
from PIL import Image

from trafficguard import analysis
from trafficguard.analysis import analyze_vehicle_input, classify_vehicle_detections, pick_best_plate
from trafficguard.ocr.ocr_engine import OcrEngine


def test_pick_best_plate_prefers_valid_indian_plate():
    best = pick_best_plate(["unknown", "KA-01-AB-1234", "HELLO123"])
    assert best.cleaned_text == "KA01AB1234"
    assert best.valid_format is True


def test_pick_best_plate_joins_adjacent_ocr_segments():
    best = pick_best_plate(
        [
            {"text": "KA01", "confidence": 0.84, "bounding_box": (10, 10, 48, 24)},
            {"text": "AB1234", "confidence": 0.9, "bounding_box": (50, 10, 112, 24)},
        ]
    )
    assert best.cleaned_text == "KA01AB1234"
    assert best.valid_format is True


def test_analyze_vehicle_input_uses_ocr_and_violation_type():
    analysis = analyze_vehicle_input("KA 01 AB 1234", violation_type="red_light")
    assert analysis["plate"] == "KA01AB1234"
    assert analysis["violation_type"] == "red_light"
    assert analysis["status"] == "ready"
    assert "KA01AB1234" in analysis["ai_analysis"]
    assert "cannot confirm" in analysis["ai_analysis"].lower()


def test_classify_vehicle_detections_maps_model_classes_to_wheel_categories():
    detection = SimpleNamespace(class_name="motorcycle", confidence=0.91)
    assert classify_vehicle_detections([detection]) == {
        "vehicle_class": "motorcycle",
        "wheel_category": "2-wheeler",
        "vehicle_confidence": 91,
    }


def test_analyze_image_includes_vehicle_classification(monkeypatch):
    class FakeOcrEngine:
        def read_text(self, image):
            return []

    class FakeDetector:
        def detect(self, image):
            return [SimpleNamespace(class_name="truck", confidence=0.88)]

    monkeypatch.setattr(analysis, "OcrEngine", FakeOcrEngine)
    image_buffer = io.BytesIO()
    Image.new("RGB", (16, 16), "white").save(image_buffer, format="PNG")

    result = analyze_vehicle_input(image_buffer.getvalue(), vehicle_detector=FakeDetector())

    assert result["vehicle_class"] == "truck"
    assert result["wheel_category"] == "6+ wheels (estimated)"
    assert result["vehicle_confidence"] == 88
    assert "truck" in result["ai_analysis"]


def test_unreadable_image_is_review_needed_without_invented_confidence(monkeypatch):
    class FakeOcrEngine:
        def read_text(self, image):
            return []

    class FakeDetector:
        def detect(self, image):
            return []

    monkeypatch.setattr(analysis, "OcrEngine", FakeOcrEngine)
    image_buffer = io.BytesIO()
    Image.new("RGB", (16, 16), "white").save(image_buffer, format="PNG")

    result = analyze_vehicle_input(image_buffer.getvalue(), vehicle_detector=FakeDetector())

    assert result["plate"] == "UNKNOWN"
    assert result["status"] == "review_needed"
    assert result["confidence"] == 0


def test_ocr_engine_reuses_easyocr_reader(monkeypatch):
    reader_instances = []

    class FakeReader:
        def __init__(self, languages, gpu):
            reader_instances.append(self)

    monkeypatch.setattr(OcrEngine, "_reader_cache", {})
    monkeypatch.setitem(sys.modules, "easyocr", SimpleNamespace(Reader=FakeReader))

    OcrEngine().initialize()
    OcrEngine().initialize()

    assert len(reader_instances) == 1


def test_ocr_engine_upscales_and_returns_full_bounding_boxes():
    class FakeReader:
        def __init__(self):
            self.image_shapes = []

        def readtext(self, image):
            self.image_shapes.append(image.shape)
            return [([[20, 20], [120, 20], [120, 60], [20, 60]], "KA01AB1234", 0.9)]

    engine = OcrEngine()
    engine._reader = FakeReader()

    results = engine.read_text(np.zeros((200, 400, 3), dtype=np.uint8))

    assert len(engine._reader.image_shapes) == 3
    assert engine._reader.image_shapes[0][:2] == (400, 800)
    assert results[0].bounding_box == (10, 10, 60, 30)
