import inspect
import os
import sys

import pytest

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover - fallback for Python < 3.11
    import tomli as tomllib

from envtoml import __version__, load, loads

SIMPLE_OUTPUT = {'x': 5, 'y': 10}
MORE_COMPLEX_OUTPUT = {
    'fruit': [
        {'name': 'apple', 'price': 2},
        {'name': 'orange', 'price': 3.14}
    ],
    'other': [
        {'name': 'laptop:1000', 'price': 1000, 'sold': True},
        {'name': 'phone', 'price': 500}
    ]
}


def test_version():
    assert __version__ == '0.4.0'


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


def test_loads_with_replace_and_fail_on_missing():
    with pytest.raises(ValueError):
        loads("x = 5\ny = '$NON_EXISTENT_VAR'\n", fail_on_missing=True)


def test_loads_with_replace_dict():
    os.environ['MY_CONFIG_VAR'] = "{z = 123}"
    assert loads("x = 5\ny = '$MY_CONFIG_VAR'\n") == {'x': 5, 'y': {'z': 123}}


def test_loads_with_multiple_replacements_in_string():
    os.environ['MONGO_USER'] = 'user01'
    os.environ['MONGO_PASS'] = 'pass01'
    os.environ['MONGO_PORT'] = '27017'
    expected = (
        'mongodb://user01:pass01@mongo:27017'
    )
    assert (
        loads(
            "mongo_url = 'mongodb://$MONGO_USER:$MONGO_PASS@mongo:$MONGO_PORT'\n"
        )
        == {'mongo_url': expected}
    )


def test_loads_with_replace_and_literal_text():
    os.environ['API_TOKEN'] = 'abc123'
    assert loads("token = 'prefix-$API_TOKEN-suffix'\n") == {
        'token': 'prefix-abc123-suffix'
    }


def test_loads_with_repeated_variable():
    os.environ['REPEAT_VAR'] = 'repeat'
    assert loads("value = '$REPEAT_VAR:$REPEAT_VAR'\n") == {
        'value': 'repeat:repeat'
    }


def test_loads_with_adjacent_variables():
    os.environ['ADJ_A'] = 'foo'
    os.environ['ADJ_B'] = 'bar'
    assert loads("value = '$ADJ_A$ADJ_B'\n") == {'value': 'foobar'}


def test_loads_with_multiple_replacements_missing_fails():
    os.environ['OK_VAR'] = 'ok'
    if 'MISSING_VAR' in os.environ:
        del os.environ['MISSING_VAR']
    with pytest.raises(ValueError):
        loads("value = '$OK_VAR:$MISSING_VAR'\n", fail_on_missing=True)


def test_loads_with_empty_variable_fails():
    os.environ['EMPTY_VAR'] = ''
    with pytest.raises(ValueError):
        loads("value = '$EMPTY_VAR'\n", fail_on_missing=True)


def test_loads_with_default_for_missing_variable():
    if 'DEFAULTED_VAR' in os.environ:
        del os.environ['DEFAULTED_VAR']
    assert loads("value = '${DEFAULTED_VAR:-fallback}'\n") == {
        'value': 'fallback'
    }


def test_loads_with_default_ignored_when_set():
    os.environ['DEFAULTED_VAR'] = 'present'
    assert loads("value = '${DEFAULTED_VAR:-fallback}'\n") == {
        'value': 'present'
    }


def test_loads_with_default_used_for_empty_value():
    os.environ['DEFAULTED_EMPTY'] = ''
    assert loads("value = '${DEFAULTED_EMPTY:-fallback}'\n") == {
        'value': 'fallback'
    }


def test_loads_with_default_and_fail_on_missing():
    if 'DEFAULTED_REQUIRED' in os.environ:
        del os.environ['DEFAULTED_REQUIRED']
    assert loads(
        "value = '${DEFAULTED_REQUIRED:-fallback}'\n", fail_on_missing=True
    ) == {'value': 'fallback'}


def test_loads_with_escaped_dollar():
    assert loads("value = '$$NOT_A_VAR'\n") == {'value': '$NOT_A_VAR'}


def test_loads_with_escaped_dollar_and_env_var():
    os.environ['ESCAPED_VAR'] = 'value'
    assert loads("value = '$$ESCAPED-$ESCAPED_VAR'\n") == {
        'value': '$ESCAPED-value'
    }


def test_loads_with_escaped_missing_and_fail_on_missing():
    if 'ESCAPED_MISSING' in os.environ:
        del os.environ['ESCAPED_MISSING']
    assert loads("value = '$$ESCAPED_MISSING'\n", fail_on_missing=True) == {
        'value': '$ESCAPED_MISSING'
    }


def test_loads_with_list_replacements():
    os.environ['LIST_VAR'] = 'list-value'
    assert loads(
        "values = ['$LIST_VAR', 'prefix-$LIST_VAR']\n"
    ) == {'values': ['list-value', 'prefix-list-value']}


def test_loads_parse_float_with_env_value():
    os.environ['FLOAT_VAR'] = '3.14'
    value = loads(
        "value = '$FLOAT_VAR'\n", parse_float=lambda s: float(s) + 1.0
    )['value']
    assert value == pytest.approx(4.14)


def _signature_params(func):
    try:
        return list(inspect.signature(func).parameters.values())
    except (TypeError, ValueError):
        return None


def _annotations(func):
    get_ann = getattr(inspect, 'get_annotations', None)
    if get_ann is None:
        return getattr(func, '__annotations__', {})
    return get_ann(func)


def test_load_signature_matches_tomllib():
    if tomllib.__name__ != 'tomllib':
        pytest.skip('stdlib tomllib not available on this Python version')
    toml_params = _signature_params(tomllib.load)
    envtoml_params = _signature_params(load)
    assert toml_params is not None
    assert envtoml_params is not None
    envtoml_map = {param.name: param for param in envtoml_params}
    for param in toml_params:
        assert param.name in envtoml_map
        assert envtoml_map[param.name].kind == param.kind
        assert envtoml_map[param.name].default == param.default


def test_loads_signature_matches_tomllib():
    if tomllib.__name__ != 'tomllib':
        pytest.skip('stdlib tomllib not available on this Python version')
    toml_params = _signature_params(tomllib.loads)
    envtoml_params = _signature_params(loads)
    assert toml_params is not None
    assert envtoml_params is not None
    envtoml_map = {param.name: param for param in envtoml_params}
    for param in toml_params:
        assert param.name in envtoml_map
        assert envtoml_map[param.name].kind == param.kind
        assert envtoml_map[param.name].default == param.default


def test_load_annotations_match_tomllib():
    if tomllib.__name__ != 'tomllib':
        pytest.skip('stdlib tomllib not available on this Python version')
    toml_annotations = _annotations(tomllib.load)
    envtoml_annotations = _annotations(load)
    for name, annotation in toml_annotations.items():
        assert envtoml_annotations.get(name) == annotation


def test_loads_annotations_match_tomllib():
    if tomllib.__name__ != 'tomllib':
        pytest.skip('stdlib tomllib not available on this Python version')
    toml_annotations = _annotations(tomllib.loads)
    envtoml_annotations = _annotations(loads)
    for name, annotation in toml_annotations.items():
        assert envtoml_annotations.get(name) == annotation


def test_load_docstring_mentions_parameters():
    doc = inspect.getdoc(load)
    assert doc is not None
    assert 'fp' in doc
    assert 'parse_float' in doc
    assert 'fail_on_missing' in doc


def test_loads_docstring_mentions_parameters():
    doc = inspect.getdoc(loads)
    assert doc is not None
    assert 's' in doc
    assert 'parse_float' in doc
    assert 'fail_on_missing' in doc


def test_loads_rejects_non_string():
    with pytest.raises((TypeError, AttributeError)):
        loads(123)  # type: ignore[arg-type]
