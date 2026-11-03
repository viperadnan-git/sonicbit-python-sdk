from json import JSONDecodeError
from typing import List

from pydantic import BaseModel, Field

from sonicbit.errors import InvalidResponseError, SonicBitError
from sonicbit.models.torrent.torrent_file import TorrentFile


class TorrentDetails(BaseModel):
    """Torrent file list from ``POST /api/seedbox/details``.

    Payload: ``{"ok": bool, "files": [...], "trackers": [...]}``. A torrent
    whose metadata has not resolved yet returns ``ok=false`` with empty
    lists — surfaced as an empty details object rather than an error.
    """

    files: List[TorrentFile]
    trackers: List[dict] = Field(default_factory=list)
    raw: dict = Field(exclude=True)

    @staticmethod
    def from_response(response, torrent_name: str = "") -> "TorrentDetails":
        try:
            json_data = response.json()
        except JSONDecodeError:
            raise InvalidResponseError(
                f"Server returned invalid JSON data: {response.text}"
            ) from None

        if msg := json_data.get("msg"):
            raise SonicBitError(f"Failed to get torrent details: {msg}")

        if "files" not in json_data:
            raise SonicBitError(
                f"Unexpected torrent details response: {str(json_data)[:200]}"
            )

        return TorrentDetails(
            files=[
                TorrentFile.from_dict(f, torrent_name=torrent_name)
                for f in json_data.get("files") or []
            ],
            trackers=list(json_data.get("trackers") or []),
            raw=json_data,
        )

    def __str__(self) -> str:
        return self.model_dump_json(indent=4)
