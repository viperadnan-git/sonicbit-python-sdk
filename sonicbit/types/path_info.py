import json
from dataclasses import dataclass
from typing import List

from sonicbit.utils import EnhancedJSONEncoder


@dataclass
class PathInfoItem:
    key: str
    name: str

    def __str__(self):
        return json.dumps(self, indent=4, cls=EnhancedJSONEncoder)


@dataclass
class PathInfo:
    paths: List[PathInfoItem]
    raw: List[dict]

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
        return json.dumps(self, indent=4, cls=EnhancedJSONEncoder)

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
