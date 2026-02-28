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
        self._refresh_lock = threading.Lock()  # prevents concurrent token refreshes
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
            with self._refresh_lock:
                logger.debug("Received 401, refreshing token for email=%s", self._email)
                self._refresh_token()
                response = super()._request(*args, **kwargs)

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
