class SonicBitError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class AuthError(SonicBitError):
    """Raised when the user is not authenticated."""


class InvalidResponseError(SonicBitError):
    """Raised when the server returns an invalid response."""

    @classmethod
    def from_response(cls, response, message: str = "Server returned invalid JSON"):
        """Build an InvalidResponseError with diagnostic context from an httpx Response."""
        return cls(
            f"{message}: {response.status_code} {response.reason_phrase} "
            f"content-type={response.headers.get('content-type', 'none')} "
            f"body={response.text[:200]}"
        )
