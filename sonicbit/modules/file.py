import json
import logging

from requests import Session

from sonicbit.enums import FileCommand
from sonicbit.modules.base import SonicBitBase
from sonicbit.types import File as FileType
from sonicbit.types import FileList, PathInfo

logger = logging.getLogger(__name__)


class File(SonicBitBase):
    def list_files(self, path: PathInfo = PathInfo.root()) -> FileList:
        logger.debug(f"Listing files in {path.path}")
        params = {
            "arguments": json.dumps({"pathInfo": path.serialized}),
            "command": FileCommand.GET_DIR_CONTENTS.value,
        }

        response = self.session.get(self.url("/file-manager"), params=params)
        return FileList.from_response(self, response)

    def delete_file(
        self, file: FileType | PathInfo, is_directory: bool = False
    ) -> bool:
        logger.debug(f"Deleting file {file.path_info.path}")
        if isinstance(file, FileType):
            is_directory = file.is_directory
            file = file.path_info

        data = {
            "arguments": json.dumps(
                {"pathInfo": file.serialized, "isDirectory": is_directory}
            ),
            "command": FileCommand.REMOVE.value,
        }

        response = self.session.post(self.url("/file-manager"), data=data)
        json_data = response.json()
        return json_data.get("success", False)
