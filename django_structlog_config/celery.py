from celery import Celery
import logging
from django.dispatch import receiver
import structlog
from celery.signals import setup_logging
from django_structlog.celery import signals

from django_structlog.celery.steps import DjangoStructLogInitStep

from .common import configure_structlog, build_formatter

def configure_celery_for_structlog(app: Celery):
    app.steps['worker'].add(DjangoStructLogInitStep)

@setup_logging.connect
def receiver_setup_logging(loglevel, logfile, format, colorize, **kwargs):  # pragma: no cover
    logging.config.dictConfig(
        {
           "version": 1,
           "disable_existing_loggers": False,
           "formatters": {
               "console_formatter": build_formatter(),
           },
           "handlers": {
               "console": {
                   "class": "logging.StreamHandler",
                   "formatter": "console_formatter",
               },
           },
            "root": {
                "handlers": ["console"],
                "level": "INFO",
            }
       }
    )

    configure_structlog()

@receiver(signals.bind_extra_task_metadata)
def receiver_bind_extra_request_metadata(sender, signal, task=None, logger=None, **kwargs):
    structlog.contextvars.bind_contextvars(correlation_id=task.request.correlation_id)
