import logging
import sys
from enum import StrEnum

from app.settings.env import env_settings


class LogLevel(StrEnum):
    DEBUG = "debug"
    INFO = "info"
    ERROR = "error"
    CRITICAL = "critical"


def get_log_level(log_level: LogLevel) -> int:
    return {
        LogLevel.DEBUG: logging.DEBUG,
        LogLevel.ERROR: logging.ERROR,
        LogLevel.INFO: logging.INFO,
        LogLevel.CRITICAL: logging.CRITICAL,
    }[log_level]


def get_logger() -> logging.Logger:
    log_level = get_log_level(LogLevel(env_settings.log_level))

    name = "app"
    new_logger = logging.getLogger(name)
    new_logger.handlers = []
    stdout = logging.StreamHandler(sys.stdout)
    fmt = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )
    stdout.setFormatter(fmt)
    stdout.setLevel(log_level)
    new_logger.addHandler(stdout)
    new_logger.setLevel(log_level)
    new_logger.propagate = False

    return new_logger


logger = get_logger()
