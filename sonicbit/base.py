from requests import Session

from sonicbit.constants import Constants


class SonicBitBase:
    """Base class for all SonicBit modules."""

    session = Session

    @staticmethod
    def url(path: str) -> str:
        return f"{Constants.API_BASE_URL}{path}"
