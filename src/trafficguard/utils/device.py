"""Device-selection helpers for inference."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def select_device() -> str:
    """Return the best available inference device.

    Prefers CUDA when available and falls back to CPU otherwise.
    """
    try:
        import torch

        if torch.cuda.is_available():
            device = "cuda"
            logger.info("Device selected: CUDA")
            return device
    except Exception:
        pass

    logger.info("Device selected: CPU")
    return "cpu"
