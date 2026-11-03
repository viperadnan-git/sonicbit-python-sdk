from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field

from sonicbit.base import SonicBitBase
from sonicbit.models.torrent.torrent_file import TorrentFile


class Torrent(BaseModel):
    """A seedbox torrent entry from ``GET /api/seedbox/list``.

    Source keys: ``id`` (infohash), ``name``, ``pct`` (0-100), ``status`` (str),
    ``statusCodes`` (list), ``dl``/``ul`` (bytes/s), ``addedTs`` (unix),
    ``sizeText``, ``priv``, ``multiFile``.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    client: SonicBitBase = Field(exclude=True)
    name: str
    hash: str
    size: int = 0
    size_text: str = ""
    progress: int
    download_rate: float = 0.0
    upload_rate: float = 0.0
    ratio: float = 0.0
    peers: int = 0
    seeds: int = 0
    date_added: datetime
    is_multi_file: bool
    status: List[str]
    is_private: bool

    raw: dict = Field(exclude=True)

    def __str__(self) -> str:
        return self.model_dump_json(indent=4)

    @property
    def files(self) -> List[TorrentFile]:
        return self.client.get_torrent_details(self.hash).files

    def delete(self, with_file: bool = False) -> bool:
        deleted_hash = self.client.delete_torrent(self.hash, with_file)
        return deleted_hash == [self.hash]
