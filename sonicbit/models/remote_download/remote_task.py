from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from sonicbit.base import SonicBitBase
from sonicbit.models.path_info import PathInfo


class RemoteTask(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    client: SonicBitBase = Field(exclude=True)
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
    raw: dict = Field(exclude=True)

    def __str__(self) -> str:
        return self.model_dump_json(indent=4)

    def delete(self) -> bool:
        return self.client.delete_remote_download(self.id)
