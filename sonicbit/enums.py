from enum import StrEnum


class FileCommand(StrEnum):
    GET_DIR_CONTENTS = "GetDirContents"
    REMOVE = "Remove"


class TorrentCommand(StrEnum):
    ADD_TORRENT_URL = "addTorrentByURL"
    DELETE_TORRENT = "deleteTorrent"
    UPLOAD_TORRENT_FILE = "UploadTorrentFile"


class RemoteDownloadCommand(StrEnum):
    LIST_REMOTE_DOWNLOADS = "get_rdl_task_list"
