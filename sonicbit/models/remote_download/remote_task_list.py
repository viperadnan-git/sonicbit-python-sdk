from json import JSONDecodeError

from pydantic import BaseModel, ConfigDict, Field

from sonicbit.base import SonicBitBase
from sonicbit.errors import InvalidResponseError
from sonicbit.models.remote_download.remote_task import RemoteTask


class RemoteTaskList(BaseModel):
    """Remote-download task list from ``GET /api/remote-download/list``."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    client: SonicBitBase = Field(exclude=True)
    tasks: list[RemoteTask]
    raw: dict = Field(exclude=True)

    @staticmethod
    def from_response(client: SonicBitBase, response) -> "RemoteTaskList":
        try:
            json_data = response.json()
        except JSONDecodeError:
            raise InvalidResponseError.from_response(response) from None

        if msg := json_data.get("msg"):
            raise InvalidResponseError(
                f"Failed to get remote download list: {msg}"
            ) from None

        tasks_data = json_data.get("tasks")
        if tasks_data is None:
            tasks_data = json_data.get("list") or []

        return RemoteTaskList(
            client=client,
            tasks=[RemoteTask.from_dict(client, t) for t in tasks_data],
            raw=json_data,
        )

    def __str__(self) -> str:
        return self.model_dump_json(indent=4)
