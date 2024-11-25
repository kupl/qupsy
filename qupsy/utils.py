import logging

from rich.console import Console
from rich.logging import RichHandler

console = Console()
_hander = RichHandler(console=console, show_path=False)
_hander.setFormatter(logging.Formatter(fmt="%(message)s", datefmt="[%X]"))
logger = logging.getLogger("quspy")
logger.addHandler(_hander)
