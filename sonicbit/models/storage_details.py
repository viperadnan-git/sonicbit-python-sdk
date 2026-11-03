from json import JSONDecodeError

from pydantic import BaseModel, Field

from sonicbit.errors import InvalidResponseError, SonicBitError


class StorageDetails(BaseModel):
    """Storage usage from ``GET /api/storage/details``.

    New payload: ``{"usedBytes": .., "totalBytes": .., "stats": {..}, "breakdown": []}``.
    Legacy field names are kept as properties for backwards compatibility
    (``size_byte_total`` was the *used* byte count in the old API).
    """

    used_bytes: int
    total_bytes: int
    percent: float
    stats: dict = Field(default_factory=dict)
    breakdown: list = Field(default_factory=list)
    raw: dict = Field(exclude=True)

    @staticmethod
    def from_response(response) -> "StorageDetails":
        try:
            json_data = response.json()
        except JSONDecodeError:
            raise InvalidResponseError.from_response(response) from None

        if msg := json_data.get("msg"):
            raise SonicBitError(f"Failed to get storage details: {msg}")

        used = int(json_data.get("usedBytes", 0))
        total = int(json_data.get("totalBytes", 0))
        percent = round(used / total * 100, 2) if total else 0.0

        return StorageDetails(
            used_bytes=used,
            total_bytes=total,
            percent=percent,
            stats=json_data.get("stats", {}),
            breakdown=json_data.get("breakdown", []),
            raw=json_data,
        )

    @property
    def size_byte_total(self) -> int:
        """Legacy alias for :attr:`used_bytes` (old API semantics)."""
        return self.used_bytes

    @property
    def size_byte_limit(self) -> int:
        """Legacy alias for :attr:`total_bytes`."""
        return self.total_bytes

    def __str__(self):
        return self.model_dump_json(indent=4)
