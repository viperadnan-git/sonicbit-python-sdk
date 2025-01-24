import logging

from sonicbit.client import SonicBit

__version__ = "0.3.0"
__all__ = ["SonicBit"]

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
