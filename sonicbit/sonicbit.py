from sonicbit.handlers.token_file_handler import TokenFileHandler
from sonicbit.handlers.token_handler import TokenHandler
from sonicbit.modules.auth import Auth
from sonicbit.modules.file import File
from sonicbit.modules.remote_download import RemoteDownload
from sonicbit.modules.torrent import Torrent
from sonicbit.modules.user import User
from sonicbit.modules.signup import Signup


class SonicBit(Auth, Signup, User, File, Torrent, RemoteDownload):
    def __init__(
        self,
        email: str,
        password: str,
        token: str = None,
        token_handler: TokenHandler = TokenFileHandler(),
    ):
        super().__init__(email, password, token, token_handler)
