from enum import Enum


class FileCommand(str, Enum):
    GET_DIR_CONTENTS = "GetDirContents"
    REMOVE = "Remove"


class TorrentCommand(str, Enum):
    ADD_TORRENT_URL = "addTorrentByURL"
    DELETE_TORRENT = "deleteTorrent"


class RemoteDownloadCommand(str, Enum):
    LIST_REMOTE_DOWNLOADS = "get_rdl_task_list"
