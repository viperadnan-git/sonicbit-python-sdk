import json
from dataclasses import dataclass
from typing import List

from requests import Response

from sonicbit.error.error import SonicbitError
from sonicbit.types.torrent.torrent_file import TorrentFile
from sonicbit.utils import EnhancedJSONEncoder


@dataclass
class TorrentDetails:
    files: List[TorrentFile]
    raw: dict

    @staticmethod
    def from_response(response: Response) -> "TorrentDetails":
        json_data = response.json()

        if "message" in json_data:
            raise SonicbitError(
                f"Failed to get torrent details: {json_data['message']}"
            )

        return TorrentDetails(
            files=[
                TorrentFile(
                    name=file_data["filename"],
                    size=file_data["sizeBytes"],
                    torrent_path=file_data["tor_path"],
                    torrent_name=file_data["name"],
                    file_path=file_data["mydrive_path"],
                    progress=file_data["percentComplete"],
                    extension=file_data["ext"],
                    priority=file_data["priority"],
                    index=file_data["index"],
                    download_url=file_data["dl_url"],
                    hash_code=file_data["hash_code"],
                    raw=file_data,
                )
                for file_data in json_data
            ],
            raw=json_data,
        )

    def __str__(self) -> str:
        return json.dumps(self, indent=4, cls=EnhancedJSONEncoder)
