import logging
from typing import List

from sonicbit.base import SonicBitBase
from sonicbit.enums import TorrentCommand
from sonicbit.error import SonicbitError
from sonicbit.types import PathInfo, TorrentDetails, TorrentList

logger = logging.getLogger(__name__)


class Torrent(SonicBitBase):
    def add_torrent(
        self,
        uri: str | List[str],
        path: PathInfo = PathInfo.root(),
        auto_start: bool = True,
    ) -> List[str]:
        logger.debug(f"Adding torrent {uri} to {path.path}")

        if isinstance(uri, str):
            uri = [uri]

        params = {
            "command": TorrentCommand.ADD_TORRENT_URL.value,
            "url_list[]": uri,
            "auto_start": 1 if auto_start else 0,
            "path": path.path,
        }

        response = self.session.post(
            self.url("/app/seedbox/torrent/add"), params=params
        )
        json_data = response.json()

        added_torrents = []
        if json_data["success"]:
            for index in json_data["added"]:
                added_torrents.append(uri[index])

        if len(added_torrents) == 0:
            raise SonicbitError("Failed to add torrent")

        return added_torrents

    def list_torrents(self) -> TorrentList:
        logger.debug("Listing torrents")

        response = self.session.post(self.url("/app/seedbox/torrent/list"))

        return TorrentList.from_response(self, response)

    def get_torrent_details(self, hash: str) -> TorrentDetails:
        logger.debug(f"Getting torrent details for {hash}")

        response = self.session.post(
            self.url(f"/app/seedbox/torrent/details"), params={"hash": hash}
        )

        return TorrentDetails.from_response(response)

    def delete_torrent(
        self, hash: str | List[str], with_file: bool = False
    ) -> List[str]:
        logger.debug(f"Deleting torrent {hash}")

        if isinstance(hash, str):
            hash = [hash]

        params = {
            "command": TorrentCommand.DELETE_TORRENT.value,
            "hash_list[]": hash,
            "with_file": 1 if with_file else 0,
        }

        response = self.session.post(
            self.url("/app/seedbox/torrent/delete"), params=params
        )
        json_data = response.json()

        if "message" in json_data:
            raise SonicbitError(f"Failed to delete torrent: {json_data['message']}")

        deleted_hash = []
        for key, value in json_data.items():
            if key in hash:
                if value:
                    deleted_hash.append(key)

        if len(deleted_hash) == 0:
            raise SonicbitError("Failed to delete torrent")

        return deleted_hash
