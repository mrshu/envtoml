import os
import re
from datetime import date, datetime, time
from typing import IO, Dict, List, Match, Optional, Sequence, Type, TypeVar, Union

import toml

__version__ = '0.1.3'

RE_ENV_VAR: str = r'\$([A-Z_][A-Z0-9_]+)'
decoder = toml.TomlDecoder()

TOMLDict = Dict[str, 'TOMLValue']
TOMLList = List['TOMLValue']
TOMLPrimitive = Union[str, int, float, bool, datetime, date, time]
TOMLValue = Union[TOMLPrimitive, TOMLDict, TOMLList]
TOMLDictT = TypeVar('TOMLDictT', bound=Dict[str, TOMLValue])


def env_replace(match: Match[str]) -> str:
    env_var = match.group(1)
    return os.environ.get(env_var, '')


def _replace_env_value(value: str) -> Optional[TOMLPrimitive]:
    if not re.match(RE_ENV_VAR, value):
        return None

    replaced = re.sub(RE_ENV_VAR, env_replace, value)

    # Try to first load the value from the environment variable (i.e. make what
    # seems like a float a float, what seems like a boolean a bool and so on).
    # If that fails, fall back to string.
    try:
        parsed, _ = decoder.load_value(replaced)
    except ValueError:
        parsed, _ = decoder.load_value('"{}"'.format(replaced))

    return parsed


def process(item: Union[TOMLDict, TOMLList]) -> None:
    if isinstance(item, dict):
        for key, val in item.items():
            if isinstance(val, (dict, list)):
                process(val)
            elif isinstance(val, str):
                replaced = _replace_env_value(val)
                if replaced is not None:
                    item[key] = replaced
    elif isinstance(item, list):
        for index, val in enumerate(item):
            if isinstance(val, (dict, list)):
                process(val)
            elif isinstance(val, str):
                replaced = _replace_env_value(val)
                if replaced is not None:
                    item[index] = replaced


def load(
    f: Union[
        str,
        os.PathLike[str],
        IO[str],
        Sequence[Union[str, os.PathLike[str], IO[str]]],
    ],
    _dict: Optional[Type[TOMLDictT]] = None,
    decoder: Optional[toml.TomlDecoder] = None,
) -> TOMLDictT:
    if _dict is None:
        data = toml.load(f, decoder=decoder)
    else:
        data = toml.load(f, _dict=_dict, decoder=decoder)
    process(data)
    return data


def loads(s: str, _dict: Optional[Type[TOMLDictT]] = None) -> TOMLDictT:
    if _dict is None:
        data = toml.loads(s)
    else:
        data = toml.loads(s, _dict=_dict)
    process(data)
    return data


load.__doc__ = toml.load.__doc__
loads.__doc__ = toml.loads.__doc__
