import logging
import logging.config
from .common import common_configure_structlog, build_formatter

def configure_for_structlog():
    common_configure_structlog()

    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console_formatter": build_formatter()
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "formatter": "console_formatter",
                "class": "logging.StreamHandler",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "INFO",
        },
    })
