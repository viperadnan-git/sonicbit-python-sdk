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
    """Base class for all SonicBit modules.

    Performance / Home Assistant integration notes
    -----------------------------------------------
    * This client is **synchronous**.  When embedding in an async framework
      such as Home Assistant, wrap every call with
      ``hass.async_add_executor_job(sb.some_method, ...)`` so the HA event
      loop is never blocked.
    * REQUEST_TIMEOUT controls how long a single HTTP attempt may take before
      it is abandoned.  The default (15 s) is intentionally short so that a
      stalled server does not block HA update cycles for an unacceptable time.
    * MAX_API_RETRIES / retry wait parameters are deliberately conservative;
      raise them if the SonicBit API is known to be flaky in your environment.
    """

    MAX_API_RETRIES = 3
    # Maximum wall-clock seconds for a single HTTP request attempt.
    # Exposed as a class variable so integrations can override it easily:
    #   SonicBitBase.REQUEST_TIMEOUT = 30
    REQUEST_TIMEOUT = 15

    def __init__(self):
        transport = httpx.HTTPTransport(retries=2)
        # Set a default timeout on the client so every request is bounded.
        # Without this, a silent server hang blocks the caller indefinitely —
        # a critical problem for event-loop–based runtimes like Home Assistant.
        self.session = httpx.Client(
            transport=transport,
            timeout=self.REQUEST_TIMEOUT,
        )

    @retry(
        stop=stop_after_attempt(MAX_API_RETRIES),
        # Start retrying after 1 s and cap at 5 s.  The previous minimum of
        # 4 s was too aggressive for HA polling intervals (typically 30–60 s).
        wait=wait_exponential(multiplier=1, min=1, max=5),
        # Retry on connection failures AND timeouts so transient network
        # blips don't surface as hard errors.
        retry=retry_if_exception_type(
            (httpx.ConnectError, httpx.TimeoutException)
        ),
    )
    def _request(self, *args, **kwargs):
        return self.session.request(*args, **kwargs)

    @staticmethod
    @retry(
        stop=stop_after_attempt(MAX_API_RETRIES),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type(
            (httpx.ConnectError, httpx.TimeoutException)
        ),
    )
    def _static_request(*args, **kwargs):
        # One-shot requests (login, signup) use the class-level timeout so
        # they are also bounded even though they don't go through self.session.
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
