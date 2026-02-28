from datetime import datetime, timezone

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from sonicbit.constants import Constants


class SonicBitBase:
    """Base class for all SonicBit modules."""

    MAX_API_RETRIES = 3
    REQUEST_TIMEOUT = 15  # seconds; override at class level if needed

    def __init__(self):
        transport = httpx.HTTPTransport(retries=2)
        self.session = httpx.Client(transport=transport, timeout=self.REQUEST_TIMEOUT)

    @retry(
        stop=stop_after_attempt(MAX_API_RETRIES),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
    )
    def _request(self, *args, **kwargs):
        return self.session.request(*args, **kwargs)

    @staticmethod
    @retry(
        stop=stop_after_attempt(MAX_API_RETRIES),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
    )
    def _static_request(*args, **kwargs):
        kwargs.setdefault("timeout", SonicBitBase.REQUEST_TIMEOUT)
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
