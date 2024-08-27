import json
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from sonicbit.base import SonicBitBase
from sonicbit.types.torrent.torrent_file import TorrentFile
from sonicbit.utils import EnhancedJSONEncoder


@dataclass
class Torrent:
    client: SonicBitBase
    name: str
    hash: str
    size: int
    progress: int
    download_rate_value: float
    download_rate_unit: str
    upload_rate_value: Optional[float]
    upload_rate_unit: Optional[str]
    peers_status: str
    seeds_status: str
    date_added: datetime
    is_multi_file: bool
    status: List[str]
    is_private: bool
    in_cache: bool
    raw: dict

    def __str__(self) -> str:
        return json.dumps(self, indent=4, cls=EnhancedJSONEncoder)

    @property
    def files(self) -> List[TorrentFile]:
        return self.client.get_torrent_details(self.hash).files

    def delete(self, with_file: bool = False) -> bool:
        deleted_hash = self.client.delete_torrent(self.hash, with_file)
        return deleted_hash == [self.hash]
