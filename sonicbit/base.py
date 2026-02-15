from datetime import datetime, timezone

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential
)

from sonicbit.constants import Constants


class SonicBitBase:
    """Base class for all SonicBit modules."""

    MAX_API_RETRIES = 5

    def __init__(self):
        transport = httpx.HTTPTransport(retries=3)
        self.session = httpx.Client(transport=transport)

    @retry(
        stop=stop_after_attempt(MAX_API_RETRIES),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(httpx.ConnectError),
    )
    def _request(self, *args, **kwargs):
        return self.session.request(*args, **kwargs)

    @staticmethod
    @retry(
        stop=stop_after_attempt(MAX_API_RETRIES),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(httpx.ConnectError),
    )
    def _static_request(*args, **kwargs):
        return httpx.request(*args, **kwargs)

    @staticmethod
    def url(path: str) -> str:
        return f"{Constants.API_BASE_URL}{path}"

    @staticmethod
    def get_time_params() -> dict:
        return {
            "tzo": 0,
            "_": int(datetime.now(timezone.utc).timestamp() * 1000),
        }
