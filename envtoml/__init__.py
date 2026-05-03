from __future__ import annotations

import json
import os
import re
import sys
from datetime import date, datetime, time
from collections.abc import MutableMapping
from typing import Any, BinaryIO, Callable, Dict, List, Match, Optional, Union

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover - fallback for Python < 3.11
    import tomli as tomllib

__version__ = '0.4.0'

RE_ENV_VAR: str = (
    r'\$\$'
    r'|\$\{(?P<braced>[A-Z_][A-Z0-9_]*)(?::-(?P<default>[^}]*))?\}'
    r'|\$(?P<simple>[A-Z_][A-Z0-9_]*)'
)

TOMLDict = Dict[str, 'TOMLValue']
TOMLList = List['TOMLValue']
TOMLPrimitive = Union[str, int, float, bool, datetime, date, time]
TOMLValue = Union[TOMLPrimitive, TOMLDict, TOMLList]
ParseFloat = Callable[[str], float]
EnvironMap = Optional[MutableMapping[str, str]]


def env_replace(
    match: Match[str],
    fail_on_missing: bool,
    env_values: EnvironMap,
) -> str:
    if match.group(0) == '$$':
        return '$'
    env_var = match.group('simple') or match.group('braced')
    default = match.group('default')
    if env_values is None:
        env_values = os.environ
    value = env_values.get(env_var)
    if value:
        return value
    if default is not None:
        return default
    if fail_on_missing:
        raise ValueError(f'{env_var} not found in environment')
    return ''


def _load_inline_value(value: str, parse_float: ParseFloat) -> TOMLValue:
    data = tomllib.loads(f'v = {value}', parse_float=parse_float)
    return data['v']


def _replace_env_value(
    value: str,
    parse_float: ParseFloat,
    fail_on_missing: bool,
    env_values: EnvironMap
) -> Optional[TOMLValue]:
    if not re.search(RE_ENV_VAR, value):
        return None

    replaced = re.sub(
        RE_ENV_VAR,
        lambda match: env_replace(match, fail_on_missing, env_values),
        value,
    )

    # Try to parse the value as TOML (float, bool, inline table, etc.).
    # If that fails, fall back to a basic string.
    try:
        return _load_inline_value(replaced, parse_float)
    except tomllib.TOMLDecodeError:
        quoted = json.dumps(replaced)
        return _load_inline_value(quoted, parse_float)


def process(
    item: TOMLValue,
    parse_float: ParseFloat,
    fail_on_missing: bool,
    env_values: EnvironMap,
) -> None:
    if isinstance(item, dict):
        for key, val in item.items():
            if isinstance(val, (dict, list)):
                process(val, parse_float, fail_on_missing, env_values)
            elif isinstance(val, str):
                replaced = _replace_env_value(val, parse_float, fail_on_missing, env_values)
                if replaced is not None:
                    item[key] = replaced
    elif isinstance(item, list):
        for index, val in enumerate(item):
            if isinstance(val, (dict, list)):
                process(val, parse_float, fail_on_missing, env_values)
            elif isinstance(val, str):
                replaced = _replace_env_value(val, parse_float, fail_on_missing, env_values)
                if replaced is not None:
                    item[index] = replaced


def load(
    fp: BinaryIO,
    /,
    *,
    parse_float: ParseFloat = float,
    fail_on_missing: bool = False,
    env_values: EnvironMap = None,
) -> dict[str, Any]:
    """Parse TOML from a binary file object and replace environment variables.

    Args:
        fp: Binary file object to read.
        parse_float: Callable to parse TOML float values.
        fail_on_missing: Raise if an env var is missing or empty.
        env_values: A mapping of env variable to value to use instead of os.environ
    """
    data = tomllib.load(fp, parse_float=parse_float)
    process(data, parse_float, fail_on_missing, env_values)
    return data


def loads(
    s: str,
    /,
    *,
    parse_float: ParseFloat = float,
    fail_on_missing: bool = False,
    env_values: EnvironMap = None,
) -> dict[str, Any]:
    """Parse TOML from a string and replace environment variables.

    Args:
        s: TOML string to parse.
        parse_float: Callable to parse TOML float values.
        fail_on_missing: Raise if an env var is missing or empty.
        env_values: A mapping of env variable to value to use instead of os.environ
    """
    data = tomllib.loads(s, parse_float=parse_float)
    process(data, parse_float, fail_on_missing, env_values)
    return data
