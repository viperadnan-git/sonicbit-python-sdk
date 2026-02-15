from json import JSONDecodeError

from httpx import Response
from pydantic import BaseModel, Field

from sonicbit.errors import InvalidResponseError, SonicBitError


class StorageDetails(BaseModel):
    size_byte_total: int
    size_byte_limit: int
    set_storage_left: int
    percent: float
    max_parallel: int
    show_notice: bool
    raw: dict = Field(exclude=True)

    @staticmethod
    def from_response(response: Response) -> "StorageDetails":
        try:
            json_data = response.json()
        except JSONDecodeError:
            raise InvalidResponseError(
                f"Server returned invalid JSON data: {response.text}"
            ) from None

        if error_message := json_data.get("message"):
            raise SonicBitError(f"Failed to get storage details: {error_message}")

        data = json_data.get("data")
        if not data:
            raise SonicBitError("Invalid response: 'data' key not found.")

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
        return self.model_dump_json(indent=4)
