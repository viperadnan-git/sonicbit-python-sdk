from typing import Optional

from pydantic import BaseModel, Field


class TorrentInfo(BaseModel):
    """Aggregate seedbox stats returned with the torrent list."""

    downloading: int = 0
    seeding: int = 0
    paused: int = 0
    completed: int = 0
    download_rate: float = 0.0
    upload_rate: float = 0.0
    ratio: float = 0.0
    total_downloaded: float = 0.0
    total_uploaded: float = 0.0
    storage_used: int = 0
    storage_total: int = 0
    torrent_max_bytes: Optional[int] = None
    raw: dict = Field(default_factory=dict, exclude=True)

    @staticmethod
    def from_dict(data: dict) -> "TorrentInfo":
        return TorrentInfo(
            downloading=int(data.get("downloading", 0) or 0),
            seeding=int(data.get("seeding", 0) or 0),
            paused=int(data.get("paused", 0) or 0),
            completed=int(data.get("completed", 0) or 0),
            download_rate=float(data.get("dl", 0) or 0),
            upload_rate=float(data.get("ul", 0) or 0),
            ratio=float(data.get("ratio", 0) or 0),
            total_downloaded=float(data.get("totalDown", 0) or 0),
            total_uploaded=float(data.get("totalUp", 0) or 0),
            storage_used=int(data.get("storageUsed", 0) or 0),
            storage_total=int(data.get("storageTotal", 0) or 0),
            torrent_max_bytes=(
                int(data["torrentMaxBytes"]) if data.get("torrentMaxBytes") else None
            ),
            raw=data,
        )

    def __str__(self):
        return self.model_dump_json(indent=4)
