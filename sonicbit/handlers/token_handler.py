from sonicbit.models.auth_response import AuthResponse


class TokenHandler:
    def __init__(self):
        pass

    def write(self, email: str, auth: AuthResponse) -> None:
        print(f"{email}'s token is {auth.token}")

    def read(self, email: str) -> str | None:
        return input(f"Enter {email}'s token: ")
