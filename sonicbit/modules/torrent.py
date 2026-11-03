import logging
import os.path
from json import JSONDecodeError
from typing import List

from sonicbit.base import SonicBitBase
from sonicbit.errors import InvalidResponseError, SonicBitError
from sonicbit.models import PathInfo, TorrentDetails, TorrentList

logger = logging.getLogger(__name__)


class Torrent(SonicBitBase):
    def add_torrent(
        self,
        uri: str | List[str],
        path: PathInfo | None = None,
        auto_start: bool = True,
    ) -> List[str]:
        """Add torrent(s) by URL/magnet via ``POST /api/seedbox/add``."""
        if path is None:
            path = PathInfo.root()

        logger.debug(
            "Adding torrent uri=%s path=%s auto_start=%s", uri, path.path, auto_start
        )

        if isinstance(uri, str):
            uri = [uri]

        response = self._request(
            method="POST",
            url=self.url("/seedbox/add"),
            json={"urls": uri, "path": path.path, "autoStart": auto_start},
        )
        try:
            json_data = response.json()
        except JSONDecodeError:
            raise InvalidResponseError(
                f"Server returned invalid JSON data: {response.text}"
            ) from None

        if not json_data.get("ok", False):
            raise SonicBitError(
                f"Failed to add torrent: {json_data.get('msg', json_data)}"
            )

        return list(uri)

    def add_torrent_file(
        self,
        local_path: str,
        path: PathInfo | None = None,
        auto_start: bool = True,
    ) -> bool:
        """Upload a .torrent file via ``POST /api/seedbox/upload``."""
        if path is None:
            path = PathInfo.root()

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

        from curl_cffi import CurlMime  # noqa: PLC0415

        multipart = CurlMime()
        multipart.addpart(name="path", data=path.path.encode())
        multipart.addpart(name="autoStart", data=("1" if auto_start else "0").encode())
        with open(local_path, "rb") as torrent_file:
            multipart.addpart(
                name="file",
                filename=file_name,
                content_type="application/x-bittorrent",
                data=torrent_file.read(),
            )

        response = self._request(
            method="POST",
            url=self.url("/seedbox/upload"),
            multipart=multipart,
        )
        try:
            json_data = response.json()
        except JSONDecodeError:
            raise InvalidResponseError(
                f"Server returned invalid JSON data: {response.text}"
            ) from None

        if not json_data.get("ok", False):
            raise SonicBitError(
                f"Failed to add torrent: {json_data.get('msg', json_data)}"
            )

        logger.debug("Torrent file uploaded successfully: %s", json_data)
        return True

    def list_torrents(self) -> TorrentList:
        logger.debug("Listing all torrents")
        response = self._request(method="GET", url=self.url("/seedbox/list"))
        return TorrentList.from_response(self, response)

    def get_torrent_details(self, hash: str) -> TorrentDetails:
        logger.debug("Fetching torrent details hash=%s", hash)
        response = self._request(
            method="POST",
            url=self.url("/seedbox/details"),
            json={"id": hash},
        )
        return TorrentDetails.from_response(response)

    def delete_torrent(
        self, _hash: str | List[str], with_file: bool = False
    ) -> List[str]:
        """Delete torrent(s) via ``POST /api/seedbox/control``."""
        logger.debug("Deleting torrent hash=%s with_file=%s", _hash, with_file)

        if isinstance(_hash, str):
            _hash = [_hash]

        response = self._request(
            method="POST",
            url=self.url("/seedbox/control"),
            json={
                "action": "delete",
                "hashes": _hash,
                "withFile": with_file,
            },
        )
        json_data = response.json()

        if msg := json_data.get("msg"):
            raise SonicBitError(f"Failed to delete torrent: {msg}")
        if not json_data.get("ok", False):
            raise SonicBitError(f"Failed to delete torrent: {json_data}")

        return list(_hash)
