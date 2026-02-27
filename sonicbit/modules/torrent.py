import logging
import os.path
from json import JSONDecodeError
from typing import List

from sonicbit.base import SonicBitBase
from sonicbit.enums import TorrentCommand
from sonicbit.errors import InvalidResponseError, SonicBitError
from sonicbit.models import PathInfo, TorrentDetails, TorrentList

logger = logging.getLogger(__name__)


class Torrent(SonicBitBase):
    def add_torrent(
        self,
        uri: str | List[str],
        path: PathInfo = PathInfo.root(),
        auto_start: bool = True,
    ) -> List[str]:
        logger.debug(
            "Adding torrent uri=%s path=%s auto_start=%s", uri, path.path, auto_start
        )

        if isinstance(uri, str):
            uri = [uri]

        params = {
            "command": TorrentCommand.ADD_TORRENT_URL,
            "url_list[]": uri,
            "auto_start": 1 if auto_start else 0,
            "path": path.path,
        }
        params.update(self.get_time_params())

        response = self._request(
            method="POST", url=self.url("/app/seedbox/torrent/add"), params=params
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
        logger.debug(
            "Uploading torrent file=%s path=%s auto_start=%s",
            local_path,
            path.path,
            auto_start,
        )

        file_name = os.path.basename(local_path)
        if not os.path.isfile(local_path):
            raise SonicBitError(
                f"Failed to upload local torrent file: '{local_path}'. File does NOT exist"
            )

        # Bug fix: open the torrent file in a context manager so the file handle
        # is guaranteed to be closed once the request completes (or raises).
        # Bug fix: "path" was missing the httpx multipart tuple form (None, value);
        # every other non-file field uses (filename, data[, content_type]) where
        # filename=None signals a plain form field — "path" must follow the same
        # convention or httpx will attempt to encode the raw string as a filename.
        with open(local_path, "rb") as torrent_file:
            post_data = {
                "command": (None, TorrentCommand.UPLOAD_TORRENT_FILE),
                "file": (file_name, torrent_file, "application/octet-stream"),
                "name": (None, file_name),
                "size": (None, str(os.stat(local_path).st_size)),
                "auto_start": (None, "1" if auto_start else "0"),
                "path": (None, path.path),
            }
            response = self._request(
                method="POST",
                url=self.url("/app/seedbox/torrent/upload"),
                files=post_data,
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
        logger.debug("Listing all torrents")

        response = self._request(
            method="POST", url=self.url("/app/seedbox/torrent/list")
        )

        return TorrentList.from_response(self, response)

    def get_torrent_details(self, hash: str) -> TorrentDetails:
        logger.debug("Fetching torrent details hash=%s", hash)

        response = self._request(
            method="POST",
            url=self.url("/app/seedbox/torrent/details"),
            params={"hash": hash},
        )

        return TorrentDetails.from_response(response)

    def delete_torrent(
        self, hash: str | List[str], with_file: bool = False
    ) -> List[str]:
        logger.debug("Deleting torrent hash=%s with_file=%s", hash, with_file)

        if isinstance(hash, str):
            hash = [hash]

        params = {
            "command": TorrentCommand.DELETE_TORRENT,
            "hash_list[]": hash,
            "with_file": 1 if with_file else 0,
        }
        params.update(self.get_time_params())

        response = self._request(
            method="POST", url=self.url("/app/seedbox/torrent/delete"), params=params
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
