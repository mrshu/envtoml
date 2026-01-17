import inspect
import os
import sys

import pytest

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover - fallback for Python < 3.11
    import tomli as tomllib

from envtoml import __version__
from envtoml import load, loads


SIMPLE_OUTPUT = {'x': 5, 'y': 10}
MORE_COMPLEX_OUTPUT = {
    'fruit': [
        {'name': 'apple', 'price': 2},
        {'name': 'orange', 'price': 3.14}
    ],
    'other': [
        {'name': 'laptop', 'price': 1000, 'sold': True},
        {'name': 'phone', 'price': 500}
    ]
}


def test_version():
    assert __version__ == '0.2.1'


def test_load():
    with open('./tests/test_simple.toml', 'rb') as handle:
        assert load(handle) == SIMPLE_OUTPUT
    with open('./tests/test_complex.toml', 'rb') as handle:
        assert load(handle) == MORE_COMPLEX_OUTPUT


def test_load_with_replace():
    os.environ['MY_CONFIG_VAR'] = "10"
    with open('./tests/test_simple_replacement.toml', 'rb') as handle:
        assert load(handle) == SIMPLE_OUTPUT


def test_loads():
    assert loads('x = 5\ny = 10\n') == SIMPLE_OUTPUT


def test_loads_with_replace():
    os.environ['MY_CONFIG_VAR'] = "10"
    assert loads("x = 5\ny = '$MY_CONFIG_VAR'\n") == SIMPLE_OUTPUT


def test_loads_with_replace_str():
    os.environ['MY_STR_CONFIG_VAR'] = "Hello"
    assert loads("name = '$MY_STR_CONFIG_VAR'\n") == {'name': 'Hello'}


def test_loads_with_replace_float():
    os.environ['MY_FLOAT_CONFIG_VAR'] = "3.14"
    assert loads("val = '$MY_FLOAT_CONFIG_VAR'\n") == {'val': 3.14}


def test_loads_with_replace_bool():
    os.environ['MY_BOOL_CONFIG_VAR'] = 'true'
    assert loads("is_set = '$MY_BOOL_CONFIG_VAR'\n") == {'is_set': True}

    os.environ['MY_BOOL_CONFIG_VAR'] = 'false'
    assert loads("is_set = '$MY_BOOL_CONFIG_VAR'\n") == {'is_set': False}


def test_complex_replacement():
    os.environ['MY_LAPTOP_NAME'] = 'laptop'
    os.environ['MY_LAPTOP_PRICE'] = '1000'
    os.environ['MY_IS_LAPTOP_SOLD'] = 'true'

    with open('./tests/test_complex_replacement.toml', 'rb') as handle:
        assert load(handle) == MORE_COMPLEX_OUTPUT


def test_loads_with_replace_and_empty_value():
    assert loads("x = 5\ny = '$NON_EXISTENT_VAR'\n") == {'x': 5, 'y': ''}


def test_loads_with_replace_dict():
    os.environ['MY_CONFIG_VAR'] = "{z = 123}"
    assert loads("x = 5\ny = '$MY_CONFIG_VAR'\n") == {'x': 5, 'y': {'z': 123}}


def _signature_shape(func):
    try:
        params = inspect.signature(func).parameters.values()
    except (TypeError, ValueError):
        return None
    return [(p.name, p.kind, p.default) for p in params]


def _annotations(func):
    get_ann = getattr(inspect, 'get_annotations', None)
    if get_ann is None:
        return getattr(func, '__annotations__', {})
    return get_ann(func)


def test_load_signature_matches_tomllib():
    if tomllib.__name__ != 'tomllib':
        pytest.skip('stdlib tomllib not available on this Python version')
    assert _signature_shape(load) == _signature_shape(tomllib.load)


def test_loads_signature_matches_tomllib():
    if tomllib.__name__ != 'tomllib':
        pytest.skip('stdlib tomllib not available on this Python version')
    assert _signature_shape(loads) == _signature_shape(tomllib.loads)


def test_load_annotations_match_tomllib():
    if tomllib.__name__ != 'tomllib':
        pytest.skip('stdlib tomllib not available on this Python version')
    assert _annotations(load) == _annotations(tomllib.load)


def test_loads_annotations_match_tomllib():
    if tomllib.__name__ != 'tomllib':
        pytest.skip('stdlib tomllib not available on this Python version')
    assert _annotations(loads) == _annotations(tomllib.loads)


def test_load_docstring_mentions_parameters():
    doc = inspect.getdoc(load)
    assert doc is not None
    assert 'fp' in doc
    assert 'parse_float' in doc


def test_loads_docstring_mentions_parameters():
    doc = inspect.getdoc(loads)
    assert doc is not None
    assert 's' in doc
    assert 'parse_float' in doc


def test_loads_rejects_non_string():
    with pytest.raises((TypeError, AttributeError)):
        loads(123)  # type: ignore[arg-type]
