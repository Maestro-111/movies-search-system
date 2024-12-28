import logging.config
import os

os.makedirs("logs", exist_ok=True)

GENERAL_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "color": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s%(asctime)s | %(levelname)s | %(message)s",
            "log_colors": {
                "DEBUG": "cyan",
                "INFO": "white",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        },
        "standard": {
            "format": "%(asctime)s | %(levelname)s | %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "color",
            "stream": "ext://sys.stdout",
        },
        "file_main": {
            "class": "logging.FileHandler",
            "level": "INFO",
            "formatter": "standard",
            "filename": "logs/movies-search-system.log",
            "mode": "a",
            "encoding": "utf-8",
        },
        "file_model": {
            "class": "logging.FileHandler",
            "level": "INFO",
            "formatter": "standard",
            "filename": "logs/models.log",
            "mode": "a",
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "movies-search-system": {
            "handlers": ["console", "file_main"],
            "level": "INFO",
            "propagate": False,
        },
        "model-logger": {
            "handlers": ["console", "file_model"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

logging.config.dictConfig(GENERAL_LOGGING_CONFIG)


system_logger = logging.getLogger("movies-search-system")
model_logger = logging.getLogger("model-logger")


system_logger.info("This is an info log for the system logger.")
model_logger.debug("This is a debug log for the model logger.")

