import logging
import os.path
from typing import List

from requests.exceptions import JSONDecodeError

from sonicbit.base import SonicBitBase
from sonicbit.enums import TorrentCommand
from sonicbit.errors import InvalidResponseError, SonicBitError
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
        params.update(self.get_time_params())

        response = self.session.post(
            self.url("/app/seedbox/torrent/add"), params=params
        )
        try:
            json_data = response.json()
        except JSONDecodeError:
            raise InvalidResponseError(
                f"Server returned invalid JSON data: {response.text}"
            ) from None

        added_torrents = []
        if json_data["success"]:
            for index in json_data["added"]:
                added_torrents.append(uri[index])

        if len(added_torrents) == 0:
            raise SonicBitError("Failed to add torrent")

        return added_torrents

    def add_torrent_file(
        self,
        local_path: str,
        path: PathInfo = PathInfo.root(),
        auto_start: bool = True,
    ) -> bool:
        logger.debug(f"Adding torrent {local_path} to {path.path}")

        file_name = os.path.basename(local_path)
        if not os.path.isfile(local_path):
            raise SonicBitError(f"Failed to upload local torrent file: '{local_path}'. File does NOT exist")

        post_data = {
            'command': (None, TorrentCommand.UPLOAD_TORRENT_FILE.value),
            'file': (file_name, open(local_path, 'rb'), 'application/octet-stream'),
            'name': (None, file_name),
            'size': (None, str(os.stat(local_path).st_size)),
            'auto_start': (None, '1' if auto_start else '0'),
            'path': path.path,
        }
        response = self.session.post(
            self.url("/app/seedbox/torrent/upload"), files=post_data
        )
        try:
            json_data = response.json()
        except JSONDecodeError:
            raise InvalidResponseError(
                f"Server returned invalid JSON data: {response.text}"
            ) from None

        if not json_data["success"]:
            raise SonicBitError("Failed to add torrent: {}".format(json_data["msg"]))

        return True

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
        params.update(self.get_time_params())

        response = self.session.post(
            self.url("/app/seedbox/torrent/delete"), params=params
        )
        json_data = response.json()

        if "message" in json_data:
            raise SonicBitError(f"Failed to delete torrent: {json_data['message']}")

        deleted_hash = []
        for key, value in json_data.items():
            if key in hash:
                if value:
                    deleted_hash.append(key)

        if len(deleted_hash) == 0:
            raise SonicBitError("Failed to delete torrent")

        return deleted_hash
