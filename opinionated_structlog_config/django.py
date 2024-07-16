from .common import common_configure_structlog, build_formatter, is_sentry_installed

def configure_django_for_structlog(middleware: list[str]):
    middleware.append("django_structlog.middlewares.RequestMiddleware")

    common_configure_structlog()

    loggers = {}

    if not is_sentry_installed():
        loggers['django.request'] = {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        }

    return {
        "version": 1,
        "disable_existing_loggers": False,
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
        "loggers": loggers,
        "filters": {
            "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}
        },
        "root": {
            "handlers": ["console"],
            "level": "INFO",
        },
    }
