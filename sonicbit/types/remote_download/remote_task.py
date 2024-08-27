import json
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from sonicbit.base import SonicBitBase
from sonicbit.types.path_info import PathInfo
from sonicbit.utils import EnhancedJSONEncoder


@dataclass
class RemoteTask:
    client: SonicBitBase
    id: int
    name: str
    url: str
    mime_type: str
    download_dir: PathInfo
    md5: str
    error: Optional[str]
    progress: int
    created_at: datetime
    in_queue: bool
    raw: dict

    def __str__(self) -> str:
        return json.dumps(self, indent=4, cls=EnhancedJSONEncoder)

    def delete(self) -> bool:
        return self.client.delete_remote_download(self.id)
