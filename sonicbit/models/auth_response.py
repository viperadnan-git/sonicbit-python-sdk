from json import JSONDecodeError

from httpx import Response
from pydantic import BaseModel, Field

from sonicbit.errors import AuthError, InvalidResponseError


class AuthResponse(BaseModel):
    token: str
    session: str
    require_2fa_verification: bool
    raw: dict = Field(exclude=True)

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
        return self.model_dump_json(indent=4)
