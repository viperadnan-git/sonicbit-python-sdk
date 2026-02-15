from pydantic import BaseModel, Field


class TorrentFile(BaseModel):
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
    raw: dict = Field(exclude=True)

    def __str__(self) -> str:
        return self.model_dump_json(indent=4)
