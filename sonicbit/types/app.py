import json
from dataclasses import dataclass
from typing import Optional

from sonicbit.utils import EnhancedJSONEncoder


@dataclass
class App:
    name: str
    type: str
    name_id: str
    user_id: int
    enable: bool
    raw: dict
    restart_count: Optional[int] = None

    @staticmethod
    def from_dict(app_data: dict) -> "App":
        return App(
            name=app_data["name"],
            type=app_data["type"],
            name_id=app_data["name_id"],
            user_id=app_data["user_id"],
            enable=app_data["enable"],
            restart_count=app_data.get("restart_count"),
            raw=app_data,
        )

    def __str__(self) -> str:
        return json.dumps(self, indent=4, cls=EnhancedJSONEncoder)
