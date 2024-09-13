import json
from dataclasses import dataclass
from typing import List

from sonicbit.utils import EnhancedJSONEncoder


@dataclass
class TorrentInfo:
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
    raw: dict

    def __str__(self) -> str:
        return json.dumps(self, indent=4, cls=EnhancedJSONEncoder)
