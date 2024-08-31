import json
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from requests import Response

from sonicbit.error import SonicbitError
from sonicbit.types.app import App
from sonicbit.utils import EnhancedJSONEncoder


@dataclass
class UserDetails:
    id: int
    name: str
    email: str
    member_since: datetime
    is_premium: bool
    username: str
    is_pending: bool
    is_suspended: bool
    size_limit: int
    file_size_limit: int
    plan_id: int
    plan_name: str
    max_parallel: int
    support_public: bool
    support_private: bool
    days_left: Optional[str]
    dl_server: str
    ftp_server: str
    server_prefix: str
    seedbox_restart_limit: int
    require_pass_change: bool
    apps: List[App]
    raw: dict

    @staticmethod
    def from_response(response: Response) -> "UserDetails":
        json_data = response.json()

        user_data = json_data.get("user_data")
        if json_data.get("message") or not user_data:
            raise SonicbitError(
                f"User details not found: {json_data.get('message', json_data)}"
            )

        return UserDetails(
            id=user_data["id"],
            name=user_data["displayName"],
            email=user_data["useremail"],
            member_since=datetime.strptime(user_data["member_since"], "%d %b %Y"),
            is_premium=bool(user_data["acc_is_premium"]),
            username=user_data["username"],
            is_pending=bool(user_data["is_pending"]),
            is_suspended=bool(user_data["is_suspended"]),
            size_limit=user_data["sizeByteLimit"],
            file_size_limit=user_data["sizeByteLimitFile"],
            plan_id=user_data["plan_id"],
            plan_name=user_data.get("plan_name", user_data["accpackage"]),
            max_parallel=user_data["max_parallel"],
            support_public=user_data["plan_type_support_public"],
            support_private=user_data["plan_type_support_private"],
            days_left=user_data["days_left"] if user_data["days_left"] else None,
            dl_server=user_data["dlserver"],
            ftp_server=user_data["ftpserver"],
            server_prefix=user_data["server_prefix"],
            seedbox_restart_limit=user_data["seedbox_restart_limit"],
            require_pass_change=bool(user_data["require_pass_change"]),
            apps=[App.from_dict(app_data) for app_data in user_data["apps"]],
            raw=user_data,
        )

    def __str__(self):
        return json.dumps(self, indent=4, cls=EnhancedJSONEncoder)
