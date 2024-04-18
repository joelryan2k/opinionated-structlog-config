from celery import Celery
import logging
from django.dispatch import receiver
import structlog
from celery.signals import setup_logging
from django_structlog.celery import signals

from django_structlog.celery.steps import DjangoStructLogInitStep

def configure_celery_for_structlog(app: Celery):
    app.steps['worker'].add(DjangoStructLogInitStep)

@setup_logging.connect
def receiver_setup_logging(loglevel, logfile, format, colorize, **kwargs):  # pragma: no cover
    timestamper = structlog.processors.TimeStamper(fmt="iso")

    pre_chain = [
        timestamper,
        structlog.stdlib.add_log_level,
        structlog.stdlib.ExtraAdder(),
    ]

    logging.config.dictConfig(
        {
           "version": 1,
           "disable_existing_loggers": False,
           "formatters": {
               "json_formatter": {
                   "()": structlog.stdlib.ProcessorFormatter,
                   "processor": structlog.processors.JSONRenderer(),
                   "foreign_pre_chain": pre_chain,
               },
           },
           "handlers": {
               "console": {
                   "class": "logging.StreamHandler",
                   "formatter": "json_formatter",
               },
           },
            "root": {
                "handlers": ["console"],
                "level": "INFO",
            }
       }
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            timestamper,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

@receiver(signals.bind_extra_task_metadata)
def receiver_bind_extra_request_metadata(sender, signal, task=None, logger=None, **kwargs):
    structlog.contextvars.bind_contextvars(correlation_id=task.request.correlation_id)
