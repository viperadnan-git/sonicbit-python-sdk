from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from sonicbit.base import SonicBitBase
from sonicbit.models.torrent.torrent_file import TorrentFile


class Torrent(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    client: SonicBitBase = Field(exclude=True)
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
    deleted: bool
    deleted_reason: str | None
    raw: dict = Field(exclude=True)

    def __str__(self) -> str:
        return self.model_dump_json(indent=4)

    @property
    def files(self) -> List[TorrentFile]:
        return self.client.get_torrent_details(self.hash).files

    def delete(self, with_file: bool = False) -> bool:
        deleted_hash = self.client.delete_torrent(self.hash, with_file)
        return deleted_hash == [self.hash]
