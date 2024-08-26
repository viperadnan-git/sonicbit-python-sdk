import dataclasses
import json
from datetime import datetime

from sonicbit.modules.base import SonicBitBase


def dataclass_dict_factory(kv_pairs) -> dict:
    # remove key "raw" from kv_pairs
    return {k: v for k, v in kv_pairs if k not in ["raw", "client"]}


def dataclass_to_dict(obj):
    data = dataclasses.asdict(obj, dict_factory=dataclass_dict_factory)
    data["_"] = obj.__class__.__name__
    return data


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclass_to_dict(o)
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, SonicBitBase):
            return f"SonicBit"
        return super().default(o)
