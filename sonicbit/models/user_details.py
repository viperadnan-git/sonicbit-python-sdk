from datetime import datetime, timezone
from json import JSONDecodeError
from typing import Optional

from pydantic import BaseModel, Field

from sonicbit.errors import InvalidResponseError


class UserDetails(BaseModel):
    """Account profile from ``GET /api/account/profile``.

    Key names on the profile endpoint are not fully documented; every field
    is optional and tolerantly mapped, with the raw payload always available.
    """

    id: Optional[int] = None
    name: str = ""
    email: str = ""
    username: str = ""
    member_since: Optional[datetime] = None
    is_premium: bool = False
    size_limit: Optional[int] = None
    file_size_limit: Optional[int] = None
    plan_id: Optional[int] = None
    plan_name: str = ""
    max_parallel: Optional[int] = None
    raw: dict = Field(default_factory=dict, exclude=True)

    @staticmethod
    def from_response(response) -> "UserDetails":
        try:
            json_data = response.json()
        except JSONDecodeError:
            raise InvalidResponseError.from_response(response) from None

        if msg := json_data.get("msg"):
            raise InvalidResponseError(f"Failed to get user details: {msg}") from None

        data = json_data.get("user") or json_data.get("data") or json_data
        member_since = None
        for key in ("memberSince", "member_since", "createdTs", "createdAt"):
            if data.get(key):
                try:
                    member_since = datetime.fromtimestamp(
                        int(data[key]), tz=timezone.utc
                    )
                except (ValueError, TypeError, OSError):
                    member_since = None
                else:
                    break

        return UserDetails(
            id=data.get("id"),
            name=data.get("name", ""),
            email=data.get("email", ""),
            username=data.get("username", ""),
            member_since=member_since,
            is_premium=bool(data.get("premium") or data.get("isPremium")),
            size_limit=data.get("sizeLimit"),
            file_size_limit=data.get("fileSizeLimit"),
            plan_id=data.get("planId"),
            plan_name=data.get("planName", ""),
            max_parallel=data.get("maxParallel"),
            raw=json_data,
        )

    def __str__(self):
        return self.model_dump_json(indent=4)
