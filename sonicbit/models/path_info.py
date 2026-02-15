from typing import List

from pydantic import BaseModel, Field


class PathInfoItem(BaseModel):
    key: str
    name: str

    def __str__(self):
        return self.model_dump_json(indent=4)


class PathInfo(BaseModel):
    paths: List[PathInfoItem]
    raw: List[dict] = Field(exclude=True)

    @staticmethod
    def from_list(data: List[dict]) -> "PathInfo":
        paths = [PathInfoItem(**item) for item in data]
        return PathInfo(paths=paths, raw=data)

    @staticmethod
    def from_path_key(path_key: str) -> "PathInfo":
        name = path_key.split("/")[-1]
        return PathInfo(
            paths=[PathInfoItem(key=path_key, name=name)],
            raw=[{"key": path_key, "name": name}],
        )

    def __str__(self):
        return self.model_dump_json(indent=4)

    @property
    def serialized(self):
        return self.raw

    @property
    def path(self):
        if len(self.paths) == 0:
            return "/"
        return f"/{self.paths[-1].key}"

    @staticmethod
    def root() -> "PathInfo":
        return PathInfo(paths=[], raw=[])
