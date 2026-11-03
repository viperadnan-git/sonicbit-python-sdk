from datetime import datetime
from json import JSONDecodeError
from typing import Dict

from pydantic import BaseModel, ConfigDict, Field

from sonicbit.base import SonicBitBase
from sonicbit.errors import InvalidResponseError, SonicBitError
from sonicbit.models.torrent.torrent import Torrent
from sonicbit.models.torrent.torrent_info import TorrentInfo


class TorrentList(BaseModel):
    """Torrent list from ``GET /api/seedbox/list``."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    client: SonicBitBase = Field(exclude=True)
    torrents: Dict[str, Torrent]
    info: TorrentInfo
    raw: dict = Field(exclude=True)

    @staticmethod
    def from_response(client: SonicBitBase, response) -> "TorrentList":
        try:
            json_data = response.json()
        except JSONDecodeError:
            raise InvalidResponseError(
                f"Server returned invalid JSON data: {response.text}"
            ) from None

        if msg := json_data.get("msg"):
            raise SonicBitError(f"Failed to get torrent list: {msg}")

        torrents_data = json_data.get("torrents") or []

        torrents = {
            t["id"]: Torrent(
                client=client,
                name=t["name"],
                hash=t["id"],
                size=int(float(t.get("gb", 0) or 0) * 1024**3),
                size_text=t.get("sizeText", ""),
                progress=int(t.get("pct", 0) or 0),
                download_rate=float(t.get("dl", 0) or 0),
                upload_rate=float(t.get("ul", 0) or 0),
                ratio=float(t.get("ratio", 0) or 0),
                peers=int(t.get("peers", 0) or 0),
                seeds=int(t.get("seeds", 0) or 0),
                date_added=datetime.fromtimestamp(int(t.get("addedTs", 0) or 0)),
                is_multi_file=bool(t.get("multiFile", False)),
                status=[t.get("status", "")] + list(t.get("statusCodes") or []),
                is_private=bool(t.get("priv", False)),
                raw=t,
            )
            for t in torrents_data
        }

        return TorrentList(
            client=client,
            torrents=torrents,
            info=TorrentInfo.from_dict(json_data.get("stats") or {}),
            raw=json_data,
        )

    def __str__(self) -> str:
        return self.model_dump_json(indent=4)
