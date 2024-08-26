import json
from dataclasses import dataclass

from sonicbit.utils import EnhancedJSONEncoder


@dataclass
class TorrentFile:
    name: str
    size: int
    torrent_path: str
    torrent_name: str
    file_path: str
    progress: int
    extension: str
    priority: int
    index: int
    download_url: str
    hash_code: str
    raw: dict

    def __str__(self) -> str:
        return json.dumps(self, indent=4, cls=EnhancedJSONEncoder)
