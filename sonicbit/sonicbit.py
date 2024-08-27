from sonicbit.modules.auth import Auth
from sonicbit.modules.file import File
from sonicbit.modules.remote_download import RemoteDownload
from sonicbit.modules.torrent import Torrent
from sonicbit.modules.user import User


class SonicBit(Auth, User, File, Torrent, RemoteDownload):
    def __init__(self, email: str, password: str, token: str = None):
        super().__init__(email, password, token)
