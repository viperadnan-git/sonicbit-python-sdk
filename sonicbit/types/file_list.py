import json
from dataclasses import dataclass
from typing import List

from requests import Response
from requests.exceptions import JSONDecodeError

from sonicbit.base import SonicBitBase
from sonicbit.error import SonicbitError
from sonicbit.types.file import File
from sonicbit.utils import EnhancedJSONEncoder


@dataclass
class FileList:
    client: SonicBitBase
    items: List[File]
    raw: dict

    @staticmethod
    def from_response(client: SonicBitBase, response: Response) -> "FileList":
        try:
            json_data = response.json()
        except JSONDecodeError:
            raise SonicbitError("Invalid response")

        result = json_data.get("result", [])
        items = [File.from_dict(client, item) for item in result]
        return FileList(client=client, items=items, raw=result)

    def __str__(self):
        return json.dumps(self, indent=4, cls=EnhancedJSONEncoder)
