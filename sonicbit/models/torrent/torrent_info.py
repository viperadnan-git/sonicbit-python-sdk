from typing import List

from pydantic import BaseModel, Field


class TorrentInfo(BaseModel):
    download_rate: int
    upload_rate: str
    size_byte_total: int
    size_byte_limit: int
    percent: float
    max_parallel: int
    email: str
    ftp: str
    plan_name: str
    seedbox_status_up: bool
    hash_list: List[str]
    raw: dict = Field(exclude=True)

    def __str__(self) -> str:
        return self.model_dump_json(indent=4)
