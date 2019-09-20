__version__ = '0.1.1'

import toml
import os
import re

RE_ENV_VAR = r'\$([A-Z_][A-Z0-9_]+)'
decoder = toml.TomlDecoder()


def env_replace(x):
    env_var = x.groups()[0]
    p = os.environ.get(env_var, '')
    return p


def process(item):
    iter_ = None
    if isinstance(item, dict):
        iter_ = item.items()
    elif isinstance(item, list):
        iter_ = enumerate(item)
    else:
        return

    for i, val in iter_:
        if isinstance(val, (dict, list)):
            process(val)
        elif isinstance(val, str):
            if re.match(RE_ENV_VAR, val):
                r = re.sub(RE_ENV_VAR, env_replace, val)

                # Try to first load the value from the environment variable
                # (i.e. make what seems like a float a float, what seems like a
                # boolean a bool and so on). If that fails, fail back to
                # string.
                try:
                    item[i], _ = decoder.load_value(r)
                    continue
                except ValueError:
                    pass

                item[i], _ = decoder.load_value(f'"{r}"')


def load(*args, **kwargs):
    data = toml.load(*args, **kwargs)
    process(data)
    return data


def loads(*args, **kwargs):
    data = toml.loads(*args, **kwargs)
    process(data)
    return data
