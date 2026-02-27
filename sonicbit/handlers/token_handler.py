from sonicbit.models.auth_response import AuthResponse


class TokenHandler:
    """Abstract base class for token storage backends.

    Subclass this and pass an instance to SonicBit() to store tokens in
    a database, secrets manager, or any other medium.

    The default implementations intentionally raise NotImplementedError so
    that a forgotten subclass method produces a clear error rather than
    silently blocking on stdin/stdout (the previous behaviour used input()
    and print(), which would freeze any async event loop such as Home
    Assistant's).
    """

    def __init__(self):
        pass

    def write(self, email: str, auth: AuthResponse) -> None:
        """Persist the token returned after a successful login.

        Args:
            email: The account email used to key the stored token.
            auth:  The AuthResponse containing the new token.
        """
        raise NotImplementedError(
            f"{type(self).__name__} must implement write(email, auth)"
        )

    def read(self, email: str) -> str | None:
        """Return a previously persisted token, or None if absent.

        Args:
            email: The account email to look up.

        Returns:
            A token string if one is cached, otherwise None so the SDK
            falls back to a fresh login.
        """
        raise NotImplementedError(
            f"{type(self).__name__} must implement read(email)"
        )
