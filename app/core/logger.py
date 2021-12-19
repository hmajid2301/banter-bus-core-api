import logging

import structlog
from structlog.stdlib import BoundLogger


def setup_logger(log_level: str):
    logging.getLogger(__name__).setLevel(log_level)
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(),
            structlog.dev.ConsoleRenderer(),
            structlog.processors.JSONRenderer(indent=2, sort_keys=True),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )


def get_logger() -> BoundLogger:
    log = structlog.get_logger()
    return log
