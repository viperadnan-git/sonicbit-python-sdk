import json
from dataclasses import dataclass

from requests import Response

from sonicbit.error.error import SonicbitError
from sonicbit.utils import EnhancedJSONEncoder


@dataclass
class StorageDetails:
    size_byte_total: int
    size_byte_limit: int
    set_storage_left: int
    percent: float
    max_parallel: int
    show_notice: bool
    raw: dict

    @staticmethod
    def from_response(response: Response) -> "StorageDetails":
        json_data = response.json()

        # Check for error message
        if "message" in json_data:
            raise SonicbitError(
                f"Failed to get storage details: {json_data['message']}"
            )

        data = json_data.get("data")
        if not data:
            raise SonicbitError("Invalid response: 'data' key not found.")

        return StorageDetails(
            size_byte_total=data["sizeByteTotal"],
            size_byte_limit=data["sizeByteLimit"],
            set_storage_left=data["setStorageleft"],
            percent=data["percent"],
            max_parallel=data["max_prallel"],
            show_notice=data["showNotice"],
            raw=data,
        )

    def __str__(self):
        return json.dumps(self, indent=4, cls=EnhancedJSONEncoder)
