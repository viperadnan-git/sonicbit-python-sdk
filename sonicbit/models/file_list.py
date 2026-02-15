from json import JSONDecodeError
from typing import List

from httpx import Response
from pydantic import BaseModel, ConfigDict, Field

from sonicbit.base import SonicBitBase
from sonicbit.errors import InvalidResponseError
from sonicbit.models.file import File


class FileList(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    client: SonicBitBase = Field(exclude=True)
    items: List[File]
    raw: list = Field(exclude=True)

    @staticmethod
    def from_response(client: SonicBitBase, response: Response) -> "FileList":
        try:
            json_data = response.json()
        except JSONDecodeError:
            raise InvalidResponseError(
                f"Server returned invalid JSON data: {response.text}"
            ) from None

        result = json_data.get("result", [])
        items = [File.from_dict(client, item) for item in result]
        return FileList(client=client, items=items, raw=result)

    def __str__(self):
        return self.model_dump_json(indent=4)
