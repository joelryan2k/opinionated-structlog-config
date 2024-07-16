import os
import structlog
import logging

timestamper = structlog.processors.TimeStamper(fmt="iso")


def is_sentry_installed():
    try:
        import sentry_sdk # type: ignore
        import structlog_sentry # type: ignore
        return True
    except ImportError:
        return False


def is_django_installed():
    try:
        import django # type: ignore
        return True
    except ImportError:
        return False

def _configure_sentry():
    if not is_django_installed():
        raise Exception("Currently django is required to support sentry. This can be adjusted, it's just not ready yet.")

    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration

    from django.conf import settings
    sentry_config = settings.OPINIONATED_STRUCTLOG_CONFIG['SENTRY']

    dsn = sentry_config['DSN']
    sentry_options = sentry_config.get('OPTIONS', {})

    sentry_sdk.init(
        dsn=dsn,
        integrations=[
            LoggingIntegration(
                level=None,
                event_level=None,
            ),
        ],
        **sentry_options,
    )

def common_configure_structlog():
    sentry_processors = []

    if is_sentry_installed():
        from structlog_sentry import SentryProcessor
        sentry_processors.append(SentryProcessor(event_level=logging.ERROR))
        _configure_sentry()

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            timestamper,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
        ] + sentry_processors + [
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

def is_running_in_container():
    if not os.path.exists('/proc/self/cgroup'):
        return False
    
    if os.environ.get('STRUCTLOG_JSON'):
        return True
    
    with open('/proc/self/cgroup', 'r') as fh:
        file_contents = fh.read()

        return 'containerd' in file_contents or 'docker' in file_contents or '/ecs/' in file_contents

def build_formatter(force_json_output = False):
    pre_chain = [
        structlog.contextvars.merge_contextvars,
        timestamper,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.stdlib.ExtraAdder(),
    ]

    if force_json_output or is_running_in_container():
        processor = structlog.processors.JSONRenderer()
    else:
        processor = structlog.dev.ConsoleRenderer()

    return {
        "()": structlog.stdlib.ProcessorFormatter,
        "processor": processor,
        "foreign_pre_chain": pre_chain,
    }
