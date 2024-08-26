import json
from dataclasses import dataclass

from requests import Response

from sonicbit.error import AuthError
from sonicbit.utils import EnhancedJSONEncoder


@dataclass
class AuthResponse:
    token: str
    session: str
    require_2fa_verification: bool
    raw: dict

    @staticmethod
    def from_response(response: Response) -> "AuthResponse":
        try:
            json_data = response.json()
        except ValueError:
            raise AuthError("Invalid response")

        success = json_data.get("success", False)

        if success:
            success_data = json_data["success"]
            return AuthResponse(
                token=success_data["token"],
                session=success_data["session"],
                require_2fa_verification=success_data["require_2fa_verification"],
                raw=success_data,
            )
        else:
            raise AuthError(
                f"Login failed: {json_data.get('error')} - {json_data.get('msg')}"
            )

    def __str__(self):
        return json.dumps(self, indent=4, cls=EnhancedJSONEncoder)
