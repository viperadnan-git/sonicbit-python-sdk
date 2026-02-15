from typing import Optional

from pydantic import BaseModel, Field


class App(BaseModel):
    name: str
    type: str
    name_id: str
    user_id: Optional[int]
    enable: bool
    require_app_server: bool
    user_is_eligible: bool
    raw: dict = Field(exclude=True)
    restart_count: Optional[int] = None

    @staticmethod
    def from_dict(app_data: dict) -> "App":
        return App(
            name=app_data["name"],
            type=app_data["type"],
            name_id=app_data["name_id"],
            user_id=app_data.get("user_id"),
            enable=app_data["enable"],
            require_app_server=app_data["require_app_server"],
            user_is_eligible=app_data["user_is_eligible"],
            restart_count=app_data.get("restart_count"),
            raw=app_data,
        )

    def __str__(self) -> str:
        return self.model_dump_json(indent=4)
