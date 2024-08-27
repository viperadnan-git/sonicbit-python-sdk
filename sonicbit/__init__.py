import logging

from sonicbit.handlers.token_file import TokenFileHandler
from sonicbit.sonicbit import SonicBit

__version__ = "0.1.1"
__all__ = ["SonicBit", "TokenFileHandler"]

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
