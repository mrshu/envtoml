from __future__ import annotations

import json
import os
import re
import sys
from datetime import date, datetime, time
from typing import Any, BinaryIO, Callable, Dict, List, Match, Optional, Union

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover - fallback for Python < 3.11
    import tomli as tomllib

__version__ = '0.2.0'

RE_ENV_VAR: str = r'\$([A-Z_][A-Z0-9_]+)'

TOMLDict = Dict[str, 'TOMLValue']
TOMLList = List['TOMLValue']
TOMLPrimitive = Union[str, int, float, bool, datetime, date, time]
TOMLValue = Union[TOMLPrimitive, TOMLDict, TOMLList]
ParseFloat = Callable[[str], float]


def env_replace(match: Match[str]) -> str:
    env_var = match.group(1)
    return os.environ.get(env_var, '')


def _load_inline_value(value: str, parse_float: ParseFloat) -> TOMLValue:
    data = tomllib.loads(f'v = {value}', parse_float=parse_float)
    return data['v']


def _replace_env_value(
    value: str,
    parse_float: ParseFloat,
) -> Optional[TOMLValue]:
    if not re.match(RE_ENV_VAR, value):
        return None

    replaced = re.sub(RE_ENV_VAR, env_replace, value)

    # Try to parse the value as TOML (float, bool, inline table, etc.).
    # If that fails, fall back to a basic string.
    try:
        return _load_inline_value(replaced, parse_float)
    except tomllib.TOMLDecodeError:
        quoted = json.dumps(replaced)
        return _load_inline_value(quoted, parse_float)


def process(item: TOMLValue, parse_float: ParseFloat) -> None:
    if isinstance(item, dict):
        for key, val in item.items():
            if isinstance(val, (dict, list)):
                process(val, parse_float)
            elif isinstance(val, str):
                replaced = _replace_env_value(val, parse_float)
                if replaced is not None:
                    item[key] = replaced
    elif isinstance(item, list):
        for index, val in enumerate(item):
            if isinstance(val, (dict, list)):
                process(val, parse_float)
            elif isinstance(val, str):
                replaced = _replace_env_value(val, parse_float)
                if replaced is not None:
                    item[index] = replaced


def load(
    fp: BinaryIO,
    /,
    *,
    parse_float: ParseFloat = float,
) -> dict[str, Any]:
    """Parse TOML from a binary file object and replace environment variables.

    Args:
        fp: Binary file object to read.
        parse_float: Callable to parse TOML float values.
    """
    data = tomllib.load(fp, parse_float=parse_float)
    process(data, parse_float)
    return data


def loads(
    s: str,
    /,
    *,
    parse_float: ParseFloat = float,
) -> dict[str, Any]:
    """Parse TOML from a string and replace environment variables.

    Args:
        s: TOML string to parse.
        parse_float: Callable to parse TOML float values.
    """
    data = tomllib.loads(s, parse_float=parse_float)
    process(data, parse_float)
    return data
