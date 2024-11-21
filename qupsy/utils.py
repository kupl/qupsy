import logging
import os

from rich.console import Console
from rich.logging import RichHandler

console = Console()


_log_level = os.environ.get("LOG_LEVEL")
if _log_level is not None:
    _log_level = _log_level.upper()
    _log_level = logging.getLevelNamesMapping()[_log_level]


_hander = RichHandler(
    console=console,
    show_path=_log_level is not None and _log_level == logging.DEBUG,
)

_hander.setFormatter(logging.Formatter(fmt="%(message)s", datefmt="[%X]"))

logger = logging.getLogger("quspy")
logger.addHandler(_hander)
if _log_level is not None:
    logger.setLevel(_log_level)
