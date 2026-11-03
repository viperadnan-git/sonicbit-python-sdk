import logging
import threading

from sonicbit.base import SonicBitBase
from sonicbit.models import AuthResponse

logger = logging.getLogger(__name__)


class Auth(SonicBitBase):
    """Session-cookie authentication for the my.sonicbit.net API.

    ``POST /api/auth/login`` validates the credentials and sets the
    ``sb_jwt`` session cookie; every other endpoint authenticates with that
    cookie alone (no Bearer token anymore). A 401 from any endpoint triggers
    a single transparent re-login and request replay.
    """

    def __init__(
        self,
        email: str,
        password: str,
        token: str | None = None,  # deprecated: kept for API compatibility
        token_handler=None,  # deprecated: kept for API compatibility
    ) -> None:
        super().__init__()
        self._refresh_lock = threading.Lock()  # prevents concurrent re-logins
        self._email = email
        self._password = password
        self._logged_in = False

        if token or token_handler:
            logger.debug(
                "Ignoring deprecated token/token_handler arguments — "
                "the 2026 SonicBit API uses cookie sessions only"
            )

        self.login_session()

    # ------------------------------------------------------------------
    # Login / re-login
    # ------------------------------------------------------------------

    def login_session(self) -> AuthResponse:
        """Authenticate and store the sb_jwt session cookie on the client."""
        logger.debug("Logging in as email=%s", self._email)
        response = super()._request(
            method="POST",
            url=self.url("/auth/login"),
            json={"email": self._email, "password": self._password},
        )
        auth = AuthResponse.from_response(response)
        self._logged_in = True
        return auth

    @staticmethod
    def login(email: str, password: str) -> AuthResponse:
        """Standalone login check; returns the response without persisting a session."""
        response = SonicBitBase._static_request(
            method="POST",
            url=SonicBitBase.url("/auth/login"),
            json={"email": email, "password": password},
        )
        return AuthResponse.from_response(response)

    # ------------------------------------------------------------------
    # Request wrapper: transparent re-login on expired sessions
    # ------------------------------------------------------------------

    def _request(self, *args, **kwargs):
        response = super()._request(*args, **kwargs)

        if response.status_code == 401 and not self._url_is_login(args, kwargs):
            with self._refresh_lock:
                if self._logged_in:
                    logger.debug("Received 401, re-logging in as email=%s", self._email)
                    self._logged_in = False
                    self.login_session()
                    response = super()._request(*args, **kwargs)

        return response

    @staticmethod
    def _url_is_login(args, kwargs) -> bool:
        url = kwargs.get("url") or (args[1] if len(args) > 1 else "")
        return "/auth/login" in str(url)
