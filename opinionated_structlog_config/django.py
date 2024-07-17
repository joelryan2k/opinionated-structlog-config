import typing

from .common import common_configure_structlog, build_formatter

def configure_django_for_structlog(middleware: list[str], config: typing.Union[dict, None] = None):
    middleware.append("django_structlog.middlewares.RequestMiddleware")

    common_configure_structlog(config or {})

    return {
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
    }
