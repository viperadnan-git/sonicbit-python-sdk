import logging

from sonicbit.client import SonicBit

__version__ = "0.2.2"
__all__ = ["SonicBit"]

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
