import os
import re
from typing import Any, Dict, Match

import toml

__version__ = '0.1.3'

RE_ENV_VAR: str = r'\$([A-Z_][A-Z0-9_]+)'
decoder = toml.TomlDecoder()
_NO_REPLACEMENT = object()


def env_replace(match: Match[str]) -> str:
    env_var = match.group(1)
    return os.environ.get(env_var, '')


def _replace_env_value(value: str) -> object:
    if not re.match(RE_ENV_VAR, value):
        return _NO_REPLACEMENT

    replaced = re.sub(RE_ENV_VAR, env_replace, value)

    # Try to first load the value from the environment variable (i.e. make what
    # seems like a float a float, what seems like a boolean a bool and so on).
    # If that fails, fall back to string.
    try:
        parsed, _ = decoder.load_value(replaced)
    except ValueError:
        parsed, _ = decoder.load_value('"{}"'.format(replaced))

    return parsed


def process(item: Any) -> None:
    if isinstance(item, dict):
        for key, val in item.items():
            if isinstance(val, (dict, list)):
                process(val)
            elif isinstance(val, str):
                replaced = _replace_env_value(val)
                if replaced is not _NO_REPLACEMENT:
                    item[key] = replaced
    elif isinstance(item, list):
        for index, val in enumerate(item):
            if isinstance(val, (dict, list)):
                process(val)
            elif isinstance(val, str):
                replaced = _replace_env_value(val)
                if replaced is not _NO_REPLACEMENT:
                    item[index] = replaced


def load(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    data = toml.load(*args, **kwargs)
    process(data)
    return data


def loads(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    data = toml.loads(*args, **kwargs)
    process(data)
    return data
