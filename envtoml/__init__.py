__version__ = '0.1.2'

import toml
import os
import re

RE_ENV_VAR = r'\$([A-Z_][A-Z0-9_]+)'
decoder = toml.TomlDecoder()


def env_replace(x, fail_on_missing=False):
    env_var = x.groups()[0]
    if fail_on_missing:
        p = os.environ.get(env_var)
        if not p:
            raise ValueError(f'{env_var} not found in environment')
    else:
        p = os.environ.get(env_var, '')
    return p


def process(item, fail_on_missing=False):
    iter_ = None
    if isinstance(item, dict):
        iter_ = item.items()
    elif isinstance(item, list):
        iter_ = enumerate(item)

    def _env_replace(x):
        return env_replace(x, fail_on_missing)

    for i, val in iter_:
        if isinstance(val, (dict, list)):
            process(val)
        elif isinstance(val, str):
            if re.match(RE_ENV_VAR, val):
                r = re.sub(RE_ENV_VAR, _env_replace, val)

                # Try to first load the value from the environment variable
                # (i.e. make what seems like a float a float, what seems like a
                # boolean a bool and so on). If that fails, fail back to
                # string.
                try:
                    item[i], _ = decoder.load_value(r)
                    continue
                except ValueError:
                    pass

                item[i], _ = decoder.load_value('"{}"'.format(r))


def load(*args, fail_on_missing=False, **kwargs):
    data = toml.load(*args, **kwargs)
    process(data, fail_on_missing)
    return data


def loads(*args, fail_on_missing=False, **kwargs):
    data = toml.loads(*args, **kwargs)
    process(data, fail_on_missing)
    return data
