import json
from dataclasses import dataclass

from requests import Response
from requests.exceptions import JSONDecodeError

from sonicbit.errors import AuthError, InvalidResponseError
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
        except JSONDecodeError:
            raise InvalidResponseError(
                f"Server returned invalid JSON data: {response.text}"
            ) from None

        if success_data := json_data.get("success", False):
            return AuthResponse(
                token=success_data["token"],
                session=success_data["session"],
                require_2fa_verification=success_data["require_2fa_verification"],
                raw=success_data,
            )
        else:
            raise AuthError(
                f"Login failed: {json_data.get('error')} - {json_data.get('msg', json_data)}"
            )

    def __str__(self):
        return json.dumps(self, indent=4, cls=EnhancedJSONEncoder)
