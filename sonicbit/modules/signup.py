import logging

from sonicbit.base import SonicBitBase
from sonicbit.constants import Constants
from sonicbit.errors import SonicBitError

logger = logging.getLogger(__name__)


class Signup(SonicBitBase):
    @staticmethod
    def signup(
        name: str, email: str, password: str, otp_callback: callable = None
    ) -> bool | str:
        """Signup to SonicBit."""

        data = {
            "name": name,
            "email": email,
            "password": password,
        }

        logger.debug("Signing up name=%s email=%s", name, email)
        response = SonicBitBase._static_request(
            method="POST",
            url=SonicBitBase.url("/user/register"),
            json=data,
            headers=Constants.API_HEADERS,
        ).json()

        if response.get("success") == True:
            if otp_callback:
                otp = otp_callback(email)
                return Signup.submit_otp(otp)
            return True
        else:
            raise SonicBitError(f"Failed to signup: {response.get('msg', response)}")

    @staticmethod
    def submit_otp(otp: str) -> str:
        """Submit OTP to SonicBit."""

        otp = otp.strip()

        if not otp.isdigit() or len(otp) != 6:
            raise SonicBitError("OTP must be a 6 digit number")

        data = {"code": otp.strip(), "type": "registration", "platform": "Web_Dash_V4"}

        logger.debug("Submitting OTP code=%s", otp)
        response = SonicBitBase._static_request(
            method="POST",
            url=SonicBitBase.url("/verification/code"),
            json=data,
            headers=Constants.API_HEADERS,
        ).json()

        if response.get("success") == True:
            token = response["data"]["token"]
            Signup._complete_tutorial(token)
            return token
        else:
            raise SonicBitError(
                f"Failed to submit OTP: {response.get('msg', response)}"
            )

    @staticmethod
    def _complete_tutorial(token: str) -> bool:
        """Complete signup."""

        data = {"delete": True}

        headers = {**Constants.API_HEADERS, "Authorization": f"Bearer {token}"}

        logger.debug("Completing tutorial for token=%s...", token[:8])
        response = SonicBitBase._static_request(
            method="POST",
            url=SonicBitBase.url("/user/account/welcome_completed"),
            json=data,
            headers=headers,
        ).json()

        if response.get("success") == True:
            return True
        else:
            raise SonicBitError(
                f"Failed to complete signup: {response.get('message', response.get('msg', response))}"
            )
