import logging
import sys
from pathlib import Path


def setup_logger(name: str, log_level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))

    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def setup_file_logger(
    name: str, log_file: Path, log_level: str = "INFO"
) -> logging.Logger:
    logger = setup_logger(name, log_level)

    log_file.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(getattr(logging, log_level.upper()))

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
