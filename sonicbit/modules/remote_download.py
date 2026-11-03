import logging

from sonicbit.base import SonicBitBase
from sonicbit.errors import SonicBitError
from sonicbit.models import RemoteTaskList
from sonicbit.models.path_info import PathInfo

logger = logging.getLogger(__name__)


class RemoteDownload(SonicBitBase):
    def add_remote_download(self, url: str, path: PathInfo | None = None) -> bool:
        if path is None:
            path = PathInfo.root()

        logger.debug("Adding remote download url=%s path=%s", url, path.path)

        json_data = self._request(
            method="POST",
            url=self.url("/remote-download/add"),
            json={"url": url, "path": path.path},
        ).json()

        if not json_data.get("ok", False):
            raise SonicBitError(
                f"Failed to add remote download: {json_data.get('msg')}"
            )

        return True

    def list_remote_downloads(self) -> RemoteTaskList:
        logger.debug("Listing all remote downloads")

        response = self._request(
            method="GET", url=self.url("/remote-download/list")
        )

        return RemoteTaskList.from_response(self, response)

    def delete_remote_download(self, id: int) -> bool:
        logger.debug("Deleting remote download id=%s", id)

        json_data = self._request(
            method="POST",
            url=self.url("/remote-download/delete"),
            json={"task_id": id},
        ).json()

        if not json_data.get("ok", False):
            raise SonicBitError(
                f"Failed to delete remote download: {json_data.get('msg')}"
            )

        return True
