from curl_cffi.requests.exceptions import ConnectionError as CurlConnectionError
from curl_cffi.requests.exceptions import RequestException as RequestsError
from curl_cffi.requests.exceptions import Timeout as CurlTimeout
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from sonicbit.constants import Constants

# Transient transport failures worth retrying (connection resets, timeouts,
# TLS negotiation hiccups).
TRANSIENT_ERRORS = (RequestsError, CurlConnectionError, CurlTimeout, ConnectionError)


class SonicBitBase:
    """Base class for all SonicBit modules.

    Every request goes through a ``curl_cffi`` session impersonating a real
    browser TLS stack. This is mandatory: SonicBit filters API traffic by
    TLS fingerprint and answers non-browser clients (httpx, requests, plain
    curl) with ``403 {"msg": "This app isn't supported..."}``.
    """

    MAX_API_RETRIES = 3
    REQUEST_TIMEOUT = 15  # seconds; override at class level if needed

    def __init__(self):
        from curl_cffi.requests import Session  # noqa: PLC0415

        self.session = Session(
            impersonate=Constants.IMPERSONATE,
            timeout=self.REQUEST_TIMEOUT,
            headers=dict(Constants.API_HEADERS),
        )

    @retry(
        stop=stop_after_attempt(MAX_API_RETRIES),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type(TRANSIENT_ERRORS),
    )
    def _request(self, method: str, url: str, **kwargs):
        return self.session.request(method, url, **kwargs)

    @staticmethod
    def _static_request(method: str, url: str, **kwargs):
        """One-off request outside any client session (e.g. login)."""
        from curl_cffi.requests import Session  # noqa: PLC0415

        with Session(
            impersonate=Constants.IMPERSONATE,
            timeout=SonicBitBase.REQUEST_TIMEOUT,
            headers=dict(Constants.API_HEADERS),
        ) as session:
            return session.request(method, url, **kwargs)

    @staticmethod
    def url(path: str) -> str:
        return f"{Constants.API_BASE_URL}{path}"
