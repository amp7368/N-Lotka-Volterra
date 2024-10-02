import json
from abc import ABC, abstractmethod
from types import SimpleNamespace
from uuid import UUID

import numpy as np


class ConfigInit(ABC):
    @abstractmethod
    def on_config_load(self) -> None:
        pass


def json_obj_callback(obj):
    if isinstance(obj, np.ndarray):
        return list(obj)
    if isinstance(obj, UUID):
        return str(obj)
    return obj.__dict__


def json_dumps(json_obj, indent: bool = False, sort_keys: bool = True) -> str:
    kwargs = {}
    if indent:
        kwargs["indent"] = 4
    kwargs["sort_keys"] = sort_keys

    return json.dumps(json_obj, default=json_obj_callback, **kwargs)


def write_file(json_obj, file: str, pretty: bool = True) -> None:
    kwargs = {}
    if pretty:
        kwargs["indent"] = 4
        kwargs["sort_keys"] = pretty

    with open(file, "w") as file:
        json.dump(json_obj, file, default=json_obj_callback, **kwargs)


def merge_obj(merge_onto: object, merge_from: SimpleNamespace, path=[]):
    from_is_dict = isinstance(merge_from, dict)
    onto_is_dict = isinstance(merge_onto, dict)
    merge_from_dict: dict = merge_from if from_is_dict else merge_from.__dict__
    merge_onto_dict: dict = merge_onto if onto_is_dict else merge_onto.__dict__

    for key in merge_from_dict:
        from_val = merge_from_dict[key]
        if key in merge_onto_dict:
            # Merge the values
            onto_val = merge_onto_dict[key]
            is_obj = hasattr(onto_val, "__dict__") and hasattr(from_val, "__dict__")
            if is_obj or isinstance(onto_val, dict):
                merge_obj(
                    onto_val,
                    from_val,
                    path + [str(key)],
                )
            elif onto_val is not None and not isinstance(from_val, type(onto_val)):
                fullpath = ".".join(path + [str(key)])
                raise Exception(
                    f"Conflict at '{fullpath}'. '{onto_val}' <- '{from_val}'"
                )
            else:
                merge_onto.__dict__[key] = from_val

        else:
            # set the currently empty key
            merge_onto.__dict__[key] = from_val
    if isinstance(merge_onto, ConfigInit):
        merge_onto.on_config_load()
    return merge_onto
