from .common import configure_structlog, build_formatter

def configure_app_for_structlog(middleware: list[str]):
    middleware.append("django_structlog.middlewares.RequestMiddleware")

    configure_structlog()

    return {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "console_formatter": build_formatter()
        },
        "handlers": {
            "mail_admins": {
                "level": "ERROR",
                "filters": ["require_debug_false"],
                "class": "django.utils.log.AdminEmailHandler",
            },
            "console": {
                "level": "DEBUG",
                "formatter": "console_formatter",
                "class": "logging.StreamHandler",
            },
        },
        "loggers": {
            "django.request": {
                "handlers": ["mail_admins"],
                "level": "ERROR",
                "propagate": True,
            },
        },
        "filters": {
            "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}
        },
        "root": {
            "handlers": ["console"],
            "level": "INFO",
        },
    }
