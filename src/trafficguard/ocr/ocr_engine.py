"""OCR abstraction and default EasyOCR adapter."""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class OcrResult:
    text: str
    confidence: float
    bounding_box: tuple[int, int, int, int] | None = None


class OcrEngine:
    """Interface for OCR backends."""

    _reader_cache: dict[str, Any] = {}
    _reader_lock = threading.Lock()

    def __init__(self, backend: str = "easyocr") -> None:
        self.backend = backend
        self._reader = self._reader_cache.get(backend)

    def initialize(self) -> None:
        if self.backend != "easyocr":
            raise ValueError(f"Unsupported OCR backend: {self.backend}")
        try:
            import easyocr
        except Exception as exc:  # pragma: no cover - import guard
            raise RuntimeError("EasyOCR is not installed or failed to import") from exc
        with self._reader_lock:
            self._reader = self._reader_cache.get(self.backend)
            if self._reader is None:
                self._reader = easyocr.Reader(['en'], gpu=False)
                self._reader_cache[self.backend] = self._reader
        logger.info("OCR engine initialized: easyocr")

    def read_text(self, image: Any) -> list[OcrResult]:
        if self._reader is None:
            self.initialize()
        results: list[OcrResult] = []
        image_array = np.asarray(image)
        for variant, scale, x_offset, y_offset in self._preprocess_variants(image_array):
            try:
                raw_results = self._reader.readtext(variant)
            except Exception as exc:  # pragma: no cover - runtime safety
                logger.warning("OCR read failed: %s", exc)
                continue

            for item in raw_results:
                if len(item) < 3:
                    continue

                text, confidence, box = item[1], item[2], item[0]
                bounding_box = None
                if box is not None:
                    points = np.asarray(box, dtype=float).reshape(-1, 2)
                    bounding_box = (
                        int(points[:, 0].min() / scale + x_offset),
                        int(points[:, 1].min() / scale + y_offset),
                        int(points[:, 0].max() / scale + x_offset),
                        int(points[:, 1].max() / scale + y_offset),
                    )
                results.append(OcrResult(text=str(text), confidence=float(confidence), bounding_box=bounding_box))
        return results

    @staticmethod
    def _preprocess_variants(image: np.ndarray) -> list[tuple[np.ndarray, float, int, int]]:
        if image.ndim == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.ndim == 3 and image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)

        height, width = image.shape[:2]
        longest_side = max(height, width)
        if longest_side < 1200:
            scale = min(2.0, 1200 / longest_side)
        elif longest_side > 2200:
            scale = 2200 / longest_side
        else:
            scale = 1.0

        if scale != 1.0:
            interpolation = cv2.INTER_CUBIC if scale > 1 else cv2.INTER_AREA
            image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=interpolation)

        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        enhanced = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
        sharpened = cv2.addWeighted(enhanced, 1.5, cv2.GaussianBlur(enhanced, (0, 0), 2), -0.5, 0)
        crop_top = int(image.shape[0] * 0.4)
        lower_crop = image[crop_top:, :]
        lower_gray = cv2.cvtColor(lower_crop, cv2.COLOR_RGB2GRAY)
        lower_enhanced = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(lower_gray)
        return [
            (image, scale, 0, 0),
            (sharpened, scale, 0, 0),
            (lower_enhanced, scale, 0, int(crop_top / scale)),
        ]
