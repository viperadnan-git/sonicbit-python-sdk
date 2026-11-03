from pydantic import BaseModel, Field

from sonicbit.constants import Constants


class TorrentFile(BaseModel):
    """A file inside a torrent, from ``POST /api/seedbox/details``.

    The 2026 payload shape for file entries is not fully documented; field
    mapping is tolerant and falls back across candidate key names observed in
    the web app (``dlurl``/``drive_path`` for downloads).
    """

    name: str
    size: int = 0
    torrent_path: str = ""
    torrent_name: str = ""
    file_path: str = ""
    progress: int = 0
    extension: str = ""
    priority: int = 0
    index: int = 0
    download_url: str
    hash_code: str = ""
    raw: dict = Field(exclude=True)

    def __str__(self) -> str:
        return self.model_dump_json(indent=4)

    @staticmethod
    def from_dict(data: dict, torrent_name: str = "") -> "TorrentFile":
        name = data.get("name") or data.get("filename") or ""
        dl_url = (
            data.get("dlurl")
            or data.get("dl_url")
            or data.get("downloadUrl")
            or ""
        )
        if not dl_url and data.get("drive_path"):
            dl_url = Constants.FILES_BASE_URL + data["drive_path"]

        return TorrentFile(
            name=name,
            size=int(data.get("sizeBytes") or data.get("size") or 0),
            torrent_path=data.get("tor_path", ""),
            torrent_name=data.get("name_torrent") or torrent_name,
            file_path=data.get("mydrive_path") or data.get("drive_path", ""),
            progress=int(data.get("percentComplete") or data.get("pct") or 0),
            extension=data.get("ext", ""),
            priority=int(data.get("priority", 0) or 0),
            index=int(data.get("index", 0) or 0),
            download_url=dl_url,
            hash_code=str(data.get("hash_code", "")),
            raw=data,
        )
