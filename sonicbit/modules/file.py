import json
import logging

from sonicbit.base import SonicBitBase
from sonicbit.enums import FileCommand
from sonicbit.models import File as FileType
from sonicbit.models import FileList, PathInfo

logger = logging.getLogger(__name__)


class File(SonicBitBase):
    def list_files(self, path: PathInfo = PathInfo.root()) -> FileList:
        logger.debug("Listing files path=%s", path.path)
        params = {
            "arguments": json.dumps({"pathInfo": path.serialized}),
            "command": FileCommand.GET_DIR_CONTENTS,
        }

        response = self._request(
            method="GET", url=self.url("/file-manager"), params=params
        )
        return FileList.from_response(self, response)

    def delete_file(
        self, file: FileType | PathInfo, is_directory: bool = False
    ) -> bool:
        if isinstance(file, FileType):
            is_directory = file.is_directory
            file = file.path_info
        logger.debug("Deleting file path=%s is_directory=%s", file.path, is_directory)
        data = {
            "arguments": json.dumps(
                {"pathInfo": file.serialized, "isDirectory": is_directory}
            ),
            "command": FileCommand.REMOVE,
        }

        response = self._request(
            method="POST", url=self.url("/file-manager"), data=data
        )
        json_data = response.json()
        return json_data.get("success", False)
