import logging
from json import JSONDecodeError

from sonicbit.base import SonicBitBase
from sonicbit.errors import InvalidResponseError
from sonicbit.models import File as FileType
from sonicbit.models import FileList, PathInfo

logger = logging.getLogger(__name__)


class File(SonicBitBase):
    def list_files(self, path: PathInfo | None = None) -> FileList:
        """List My Drive contents via ``POST /api/drive/list``."""
        if path is None:
            path = PathInfo.root()

        logger.debug("Listing files path=%s", path.path)

        response = self._request(
            method="POST", url=self.url("/drive/list"), json={"path": path.path}
        )
        return FileList.from_response(self, response)

    def delete_file(
        self, file: FileType | PathInfo, is_directory: bool = False
    ) -> bool:
        """Delete a My Drive item via ``POST /api/drive/delete``."""
        inode = None
        if isinstance(file, FileType):
            is_directory = file.is_directory
            inode = file.raw.get("in")
            file = file.path_info

        logger.debug("Deleting file path=%s is_directory=%s", file.path, is_directory)

        item = {"pathInfo": file.serialized, "isDirectory": is_directory}
        if inode is not None:
            item["in"] = inode

        response = self._request(
            method="POST", url=self.url("/drive/delete"), json={"items": [item]}
        )
        try:
            json_data = response.json()
        except JSONDecodeError:
            raise InvalidResponseError.from_response(response) from None

        return bool(json_data.get("success") or json_data.get("ok"))
