import json
import os

from sonicbit.types import AuthResponse


class BaseTokenHandler:
    def __init__(self):
        pass

    def write(self, email: str, auth: AuthResponse) -> None:
        print(f"{email} sesion is {auth.sesion}")

    def read(self, email: str) -> str | None:
        return input(f"Enter {email} sesion: ")


class TokenFileHandler(BaseTokenHandler):
    def __init__(self, path: str = ".sonicbit.cache"):
        self.path = os.path.abspath(path)
        super().__init__()

    def write(self, email: str, auth: AuthResponse) -> None:
        cache = self.read_cache()

        cache[email] = auth.token
        with open(self.path, "w") as f:
            json.dump(cache, f)

    def read(self, email: str) -> str | None:
        cache = self.read_cache()

        return cache.get(email)

    def read_cache(self) -> dict:
        if os.path.exists(self.path):
            try:
                with open(self.path, "r") as f:
                    cache = json.load(f)
            except:
                raise Exception(
                    f"Invalid cache file, please delete '{self.path}' and try again"
                )
        else:
            cache = {}

        return cache
