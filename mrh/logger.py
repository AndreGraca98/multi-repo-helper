import logging
import os

from colors import fblue, fgreen, fmagenta, fred, fyellow


def get_logger(name: str):
    level_fmt = dict(
        DEBUG=fblue, INFO=fgreen, WARNING=fyellow, ERROR=fred, CRITICAL=fmagenta
    )

    class CustomFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            record.levelname = level_fmt[record.levelname](record.levelname)
            return super().format(record)

    log_level = os.environ.get("LOGGER_LEVEL", "INFO").upper()
    fmt_str = "%(levelname)s: %(message)s"
    # fmt_str = "%(asctime)s %(levelname)s: %(message)s"
    formatter = CustomFormatter(fmt=fmt_str, datefmt="%H:%M:%S")
    _logger = logging.getLogger(name)
    _logger.setLevel(log_level)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    _logger.addHandler(stream_handler)
    return _logger
