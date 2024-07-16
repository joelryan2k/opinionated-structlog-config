import logging
import logging.config
import typing

from .common import common_configure_structlog, build_formatter

def configure_for_structlog(force_json_output = False, config: typing.Union[None, dict] = None):
    common_configure_structlog(config or {})

    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console_formatter": build_formatter(force_json_output=force_json_output)
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
