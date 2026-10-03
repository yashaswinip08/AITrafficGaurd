"""OCR abstraction and default EasyOCR adapter."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class OcrResult:
    text: str
    confidence: float
    bounding_box: tuple[int, int, int, int] | None = None


class OcrEngine:
    """Interface for OCR backends."""

    def __init__(self, backend: str = "easyocr") -> None:
        self.backend = backend
        self._reader = None

    def initialize(self) -> None:
        if self.backend != "easyocr":
            raise ValueError(f"Unsupported OCR backend: {self.backend}")
        try:
            import easyocr
        except Exception as exc:  # pragma: no cover - import guard
            raise RuntimeError("EasyOCR is not installed or failed to import") from exc
        self._reader = easyocr.Reader(['en'], gpu=False)
        logger.info("OCR engine initialized: easyocr")

    def read_text(self, image: Any) -> list[OcrResult]:
        if self._reader is None:
            self.initialize()
        try:
            raw_results = self._reader.readtext(image)
        except Exception as exc:  # pragma: no cover - runtime safety
            logger.warning("OCR read failed: %s", exc)
            return []

        results: list[OcrResult] = []
        for item in raw_results:
            if len(item) >= 3:
                text, conf, box = item[1], item[2], item[0]
                results.append(OcrResult(text=str(text), confidence=float(conf), bounding_box=tuple(map(int, box[0])) if box else None))
        return results
