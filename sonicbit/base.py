from datetime import datetime, timezone

from requests import Session, request
from requests.adapters import HTTPAdapter
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
from urllib3 import Retry

from sonicbit.constants import Constants


class SonicBitBase:
    """Base class for all SonicBit modules."""

    session = Session
    MAX_API_RETRIES = 5

    def __init__(self):
        self.session = Session()

        self._requests_retry = Retry(
            connect=3,
            backoff_factor=1.5,
        )
        self._requests_adapter = HTTPAdapter(max_retries=self._requests_retry)

        self.session.mount("http://", self._requests_adapter)
        self.session.mount("https://", self._requests_adapter)

    @retry(
        stop=stop_after_attempt(MAX_API_RETRIES),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(ConnectionError),
    )
    def call(self, *args, **kwargs):
        return self.session.request(*args, **kwargs)

    @retry(
        stop=stop_after_attempt(MAX_API_RETRIES),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(ConnectionError),
    )
    @staticmethod
    def request_call(*args, **kwargs):
        return request(*args, **kwargs)

    @staticmethod
    def url(path: str) -> str:
        return f"{Constants.API_BASE_URL}{path}"

    @staticmethod
    def get_time_params() -> dict:
        return {
            "tzo": 0,
            "_": int(datetime.now(timezone.utc).timestamp() * 1000),
        }
