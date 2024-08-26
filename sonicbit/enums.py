from enum import Enum


class FileCommand(Enum):
    GET_DIR_CONTENTS = "GetDirContents"
    REMOVE = "Remove"


class TorrentCommand(Enum):
    ADD_TORRENT_URL = "addTorrentByURL"
    DELETE_TORRENT = "deleteTorrent"


class RemoteDownloadCommand(Enum):
    LIST_REMOTE_DOWNLOADS = "get_rdl_task_list"
