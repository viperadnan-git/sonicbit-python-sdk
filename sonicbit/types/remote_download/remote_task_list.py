import json
from dataclasses import dataclass
from datetime import datetime

from requests import Response

from sonicbit.base import SonicBitBase
from sonicbit.error.error import SonicbitError
from sonicbit.types.path_info import PathInfo
from sonicbit.utils import EnhancedJSONEncoder

from .remote_task import RemoteTask


@dataclass
class RemoteTaskList:
    client: SonicBitBase
    tasks: list[RemoteTask]
    raw: dict

    @staticmethod
    def from_response(client: SonicBitBase, response: Response) -> "RemoteTaskList":
        json_data = response.json()

        if "message" in json_data:
            raise SonicbitError(
                f"Failed to get remote download list: {json_data['message']}"
            )

        if not json_data.get("success", False):
            raise SonicbitError(
                f"Failed to get remote download list: {json_data['msg']}"
            )

        return RemoteTaskList(
            client=client,
            tasks=[
                RemoteTask(
                    client=client,
                    id=task_data["id"],
                    name=task_data["name"],
                    url=task_data["url"],
                    mime_type=task_data["mime_type"],
                    download_dir=PathInfo.from_path_key(task_data["download_dir"]),
                    md5=task_data["log_file_md5"],
                    error=task_data["error"],
                    progress=task_data["percent"],
                    created_at=datetime.fromtimestamp(task_data["added"]),
                    in_queue=task_data["isQueue"] == 1,
                    raw=task_data,
                )
                for task_data in json_data["tasks"]
            ],
            raw=json_data,
        )

    def __str__(self) -> str:
        return json.dumps(self, indent=4, cls=EnhancedJSONEncoder)
