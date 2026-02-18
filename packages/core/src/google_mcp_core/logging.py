from __future__ import annotations

import logging
from typing import Optional


DEFAULT_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def setup_logging(level: int = logging.INFO, fmt: str = DEFAULT_FORMAT) -> None:
    logging.basicConfig(level=level, format=fmt)


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    logger = logging.getLogger(name)
    if level is not None:
        logger.setLevel(level)
    return logger
