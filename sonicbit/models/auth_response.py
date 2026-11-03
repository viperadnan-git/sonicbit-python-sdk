from json import JSONDecodeError

from pydantic import BaseModel, Field

from sonicbit.errors import AuthError, InvalidResponseError


class AuthResponse(BaseModel):
    """Response from ``POST /api/auth/login``.

    Authentication state lives in the ``sb_jwt`` session cookie managed by
    the HTTP client; this model only reports login success/2FA state.
    """

    ok: bool
    require_2fa_verification: bool
    raw: dict = Field(exclude=True)

    @staticmethod
    def from_response(response) -> "AuthResponse":
        try:
            json_data = response.json()
        except JSONDecodeError:
            raise InvalidResponseError.from_response(response) from None

        if response.status_code == 401:
            raise AuthError(
                f"Login failed: {json_data.get('msg', json_data)} "
                f"(HTTP {response.status_code})"
            )
        if response.status_code == 403:
            raise AuthError(
                "Login blocked by SonicBit client filtering "
                f"(HTTP 403: {json_data.get('msg', 'app not supported')}) — "
                "requests must use browser TLS impersonation"
            )
        if not json_data.get("ok", False):
            raise AuthError(f"Login failed: {json_data.get('msg', json_data)}")

        return AuthResponse(
            ok=json_data["ok"],
            require_2fa_verification=bool(json_data.get("require2fa", False)),
            raw=json_data,
        )

    def __str__(self):
        return self.model_dump_json(indent=4)
