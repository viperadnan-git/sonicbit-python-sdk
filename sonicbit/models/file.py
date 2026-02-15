from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field

from sonicbit.base import SonicBitBase
from sonicbit.models.path_info import PathInfo


class File(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    client: SonicBitBase = Field(exclude=True)
    name: str
    size: int
    path: str
    drive_path: str
    path_info: PathInfo
    download_url: str
    diff_minutes: int
    date_modified_str: str
    date_modified: datetime
    is_directory: bool
    is_remote_drive_dir: bool
    raw: dict = Field(exclude=True)

    @staticmethod
    def from_dict(client: SonicBitBase, data: dict) -> "File":
        return File(
            client=client,
            name=data["name"],
            size=data["size"],
            path=data["path"],
            drive_path=data["drive_path"],
            path_info=PathInfo.from_list(data["data_drive_path"]),
            download_url=data["dlurl"],
            diff_minutes=data["diff_minutes"],
            date_modified_str=data["dateModified"],
            date_modified=datetime.fromtimestamp(data["dateModifiedTS"]),
            is_directory=data["isDirectory"],
            is_remote_drive_dir=data["isRemoteDriveDir"],
            raw=data,
        )

    def __str__(self) -> str:
        return self.model_dump_json(indent=4)

    def delete(self) -> bool:
        return self.client.delete_file(file=self, is_directory=self.is_directory)

    @property
    def items(self) -> List["File"]:
        if self.is_directory:
            return self.client.list_files(path=self.path_info).items
        return [self]
