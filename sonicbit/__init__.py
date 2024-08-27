import logging

from sonicbit.sonicbit import SonicBit

__version__ = "0.1.1"
__all__ = ["SonicBit"]

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
