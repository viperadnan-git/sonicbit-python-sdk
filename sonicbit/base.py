from requests import Session
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from sonicbit.constants import Constants


class SonicBitBase:
    """Base class for all SonicBit modules."""

    session = Session

    def __init__(self):
        self.session = Session()

        self._requests_retry = Retry(
            connect=3,
            backoff_factor=1.5,
            backoff_max=120,
        )
        self._requests_adapter = HTTPAdapter(max_retries=self._requests_retry)

        self.session.mount("http://", self._requests_adapter)
        self.session.mount("https://", self._requests_adapter)

    @staticmethod
    def url(path: str) -> str:
        return f"{Constants.API_BASE_URL}{path}"
