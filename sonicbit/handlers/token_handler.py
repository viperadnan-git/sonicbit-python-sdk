from abc import ABC, abstractmethod

from sonicbit.models.auth_response import AuthResponse


class TokenHandler(ABC):
    """Abstract base class for token storage backends.

    Subclass this and pass an instance to SonicBit() to store tokens in
    a database, secrets manager, or any other medium.
    """

    @abstractmethod
    def write(self, email: str, auth: AuthResponse) -> None:
        """Persist the token returned after a successful login.

        Args:
            email: The account email used to key the stored token.
            auth:  The AuthResponse containing the new token.
        """

    @abstractmethod
    def read(self, email: str) -> str | None:
        """Return a previously persisted token, or None if absent.

        Args:
            email: The account email to look up.

        Returns:
            A token string if one is cached, otherwise None so the SDK
            falls back to a fresh login.
        """
