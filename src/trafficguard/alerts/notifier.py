"""Alerting utilities."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class Notifier:
    """Simple notifier abstraction with console output by default."""

    def send(self, message: str) -> None:
        logger.info(message)
        print(message)
