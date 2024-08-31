import logging

from requests import Session, request

from sonicbit.base import SonicBitBase
from sonicbit.constants import Constants
from sonicbit.handlers.token_handler import TokenHandler
from sonicbit.types import AuthResponse

logger = logging.getLogger(__name__)


class Auth(SonicBitBase):
    def __init__(
        self,
        email: str,
        password: str,
        token: str | None,
        token_handler: TokenHandler,
    ):
        logger.debug("Initializing Auth")
        self.session = Session()
        self.session.headers.update(Constants.API_HEADERS)

        if not token:
            token = self.get_token(email, password, token_handler)

        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def get_token(self, email: str, password: str, token_handler: TokenHandler) -> str:
        logger.debug("Getting token")
        token = token_handler.read(email)
        if token:
            return token

        auth = self.login(email, password)
        token_handler.write(email, auth)

        return auth.token

    @staticmethod
    def login(email: str, password: str) -> AuthResponse:
        logger.info(f"Logging in as {email}")
        response = request(
            "POST",
            Auth.url("/web/login"),
            json={"email": email, "password": password},
            headers=Constants.API_HEADERS,
        )

        return AuthResponse.from_response(response)
