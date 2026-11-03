from sonicbit.modules.auth import Auth
from sonicbit.modules.file import File
from sonicbit.modules.remote_download import RemoteDownload
from sonicbit.modules.signup import Signup
from sonicbit.modules.torrent import Torrent
from sonicbit.modules.user import User


class SonicBit(Auth, Signup, User, File, Torrent, RemoteDownload):
    """SonicBit API client (2026 my.sonicbit.net platform).

    ``token``/``token_handler`` are accepted for backwards compatibility but
    ignored — the platform now authenticates with a server-managed ``sb_jwt``
    session cookie established at construction time.
    """

    def __init__(
        self,
        email: str,
        password: str,
        token: str | None = None,
        token_handler=None,
    ):
        super().__init__(email, password, token, token_handler)
