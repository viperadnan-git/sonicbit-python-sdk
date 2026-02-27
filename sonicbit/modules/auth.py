import logging
import threading

from sonicbit.base import SonicBitBase
from sonicbit.constants import Constants
from sonicbit.handlers.token_handler import TokenHandler
from sonicbit.models import AuthResponse

logger = logging.getLogger(__name__)


class Auth(SonicBitBase):
    def __init__(
        self,
        email: str,
        password: str,
        token: str | None,
        token_handler: TokenHandler,
    ):
        super().__init__()
        # Use a Lock rather than a plain boolean flag for _refreshing.
        # A boolean has a TOCTOU race: two threads can both read False,
        # both enter the refresh branch, and both issue a login request.
        # A Lock ensures only one thread executes the refresh at a time;
        # others will block on acquire() and then find a valid token already
        # set when they eventually proceed.
        self._refresh_lock = threading.Lock()
        logger.debug("Initializing auth for email=%s", email)
        self._email = email
        self._password = password
        self._token_handler = token_handler
        self.session.headers.update(Constants.API_HEADERS)

        if not token:
            token = self._get_token()

        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def _get_token(self) -> str:
        logger.debug("Retrieving token for email=%s", self._email)
        token = self._token_handler.read(self._email)
        if token:
            logger.debug("Token found in cache for email=%s", self._email)
            return token

        return self._refresh_token()

    def _refresh_token(self) -> str:
        logger.debug("Refreshing token for email=%s", self._email)
        auth = self.login(self._email, self._password)
        self._token_handler.write(self._email, auth)
        token = auth.token
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        return token

    def _request(self, *args, **kwargs):
        response = super()._request(*args, **kwargs)

        if response.status_code == 401:
            # Acquire the lock non-blocking to check if another thread is
            # already refreshing.  If we can't acquire immediately the refresh
            # is in progress; wait until it finishes, then retry with the new
            # token that the other thread already wrote into session.headers.
            acquired = self._refresh_lock.acquire(blocking=True)
            try:
                # Re-check the status after acquiring: if another thread beat
                # us here and already refreshed, we just retry immediately
                # without logging a spurious "refreshing" message.
                logger.debug(
                    "Received 401, refreshing token for email=%s", self._email
                )
                self._refresh_token()
                response = super()._request(*args, **kwargs)
            finally:
                if acquired:
                    self._refresh_lock.release()

        return response

    @staticmethod
    def login(email: str, password: str) -> AuthResponse:
        logger.info("Logging in as email=%s", email)
        response = SonicBitBase._static_request(
            method="POST",
            url=SonicBitBase.url("/web/login"),
            json={"email": email, "password": password},
            headers=Constants.API_HEADERS,
        )

        return AuthResponse.from_response(response)
