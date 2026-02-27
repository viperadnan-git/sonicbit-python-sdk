from sonicbit.handlers.token_file_handler import TokenFileHandler
from sonicbit.handlers.token_handler import TokenHandler
from sonicbit.modules.auth import Auth
from sonicbit.modules.file import File
from sonicbit.modules.remote_download import RemoteDownload
from sonicbit.modules.signup import Signup
from sonicbit.modules.torrent import Torrent
from sonicbit.modules.user import User


class SonicBit(Auth, Signup, User, File, Torrent, RemoteDownload):
    def __init__(
        self,
        email: str,
        password: str,
        token: str | None = None,
        token_handler: TokenHandler | None = None,
    ):
        # Mutable default argument fix: using `TokenFileHandler()` directly as
        # a default argument would evaluate it *once* at class-definition time,
        # causing every SonicBit instance that omits token_handler to share the
        # same TokenFileHandler object.  With multiple accounts this would mix
        # credentials.  Instead we default to None and construct a fresh
        # instance per call here.
        if token_handler is None:
            token_handler = TokenFileHandler()
        super().__init__(email, password, token, token_handler)
