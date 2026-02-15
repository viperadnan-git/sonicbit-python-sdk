import logging

from sonicbit._version import __version__
from sonicbit.client import SonicBit

logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

__all__ = ["SonicBit", "__version__"]
