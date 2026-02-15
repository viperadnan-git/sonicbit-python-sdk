import logging

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
        logger.debug("Initializing auth for email=%s", email)
        self.session.headers.update(Constants.API_HEADERS)

        if not token:
            token = self.get_token(email, password, token_handler)

        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def get_token(self, email: str, password: str, token_handler: TokenHandler) -> str:
        logger.debug("Retrieving token for email=%s", email)
        token = token_handler.read(email)
        if token:
            logger.debug("Token found in cache for email=%s", email)
            return token

        logger.debug("No cached token found for email=%s, logging in", email)
        auth = self.login(email, password)
        token_handler.write(email, auth)

        return auth.token

    @staticmethod
    def login(email: str, password: str) -> AuthResponse:
        logger.info("Logging in as email=%s", email)
        response = SonicBitBase.request_call(
            method="POST",
            url=SonicBitBase.url("/web/login"),
            json={"email": email, "password": password},
            headers=Constants.API_HEADERS,
        )

        return AuthResponse.from_response(response)
