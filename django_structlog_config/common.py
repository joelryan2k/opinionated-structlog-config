import os
import structlog

timestamper = structlog.processors.TimeStamper(fmt="iso")


def configure_structlog():
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

def is_running_in_container():
    if not os.path.exists('/proc/self/cgroup'):
        return False
    
    with open('/proc/self/cgroup', 'r') as fh:
        file_contents = fh.read()

        return 'containerd' in file_contents or 'docker' in file_contents

def build_formatter():
    pre_chain = [
        timestamper,
        structlog.stdlib.add_log_level,
        structlog.stdlib.ExtraAdder(),
    ]

    if is_running_in_container():
        processor = structlog.processors.JSONRenderer()
    else:
        processor = structlog.dev.ConsoleRenderer()

    return {
        "()": structlog.stdlib.ProcessorFormatter,
        "processor": processor,
        "foreign_pre_chain": pre_chain,
    }
