class SonicBitError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class AuthError(SonicBitError):
    """Raised when the user is not authenticated."""


class InvalidResponseError(SonicBitError):
    """Raised when the server returns an invalid response."""
