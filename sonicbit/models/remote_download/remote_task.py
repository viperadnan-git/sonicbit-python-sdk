from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from sonicbit.base import SonicBitBase


class RemoteTask(BaseModel):
    """A remote-download task from ``GET /api/remote-download/list``.

    Field mapping is tolerant — key availability varies with task state.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    client: SonicBitBase = Field(exclude=True)
    id: int
    name: str = ""
    url: str = ""
    status: str = ""
    progress: int = 0
    error: Optional[str] = None
    created_at: Optional[datetime] = None
    raw: dict = Field(exclude=True)

    def __str__(self) -> str:
        return self.model_dump_json(indent=4)

    @staticmethod
    def from_dict(client: SonicBitBase, data: dict) -> "RemoteTask":
        added = data.get("addedTs") or data.get("added")
        created = None
        if added:
            try:
                created = datetime.fromtimestamp(int(added), tz=timezone.utc)
            except (ValueError, TypeError, OSError):
                created = None

        return RemoteTask(
            client=client,
            id=int(data.get("id", 0) or 0),
            name=data.get("name", ""),
            url=data.get("url", ""),
            status=data.get("status", ""),
            progress=int(data.get("pct") or data.get("percent") or 0),
            error=data.get("error"),
            created_at=created,
            raw=data,
        )

    def delete(self) -> bool:
        return self.client.delete_remote_download(self.id)
