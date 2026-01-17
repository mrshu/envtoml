from envtoml import __version__
from envtoml import load, loads
import os


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
    assert __version__ == '0.1.3'


def test_load():
    assert load(open('./tests/test_simple.toml')) == SIMPLE_OUTPUT
    assert load(open('./tests/test_complex.toml')) == MORE_COMPLEX_OUTPUT


def test_load_with_replace():
    os.environ['MY_CONFIG_VAR'] = "10"
    assert load(open('./tests/test_simple_replacement.toml')) == SIMPLE_OUTPUT


def test_loads():
    assert loads('{x = 5, y = 10}') == SIMPLE_OUTPUT


def test_loads_with_replace():
    os.environ['MY_CONFIG_VAR'] = "10"
    assert loads("{x = 5, y = '$MY_CONFIG_VAR'}") == SIMPLE_OUTPUT


def test_loads_with_replace_str():
    os.environ['MY_STR_CONFIG_VAR'] = "Hello"
    assert loads("{name = '$MY_STR_CONFIG_VAR'}") == {'name': 'Hello'}


def test_loads_with_replace_float():
    os.environ['MY_FLOAT_CONFIG_VAR'] = "3.14"
    assert loads("{val = '$MY_FLOAT_CONFIG_VAR'}") == {'val': 3.14}


def test_loads_with_replace_bool():
    os.environ['MY_BOOL_CONFIG_VAR'] = 'true'
    assert loads("{is_set = '$MY_BOOL_CONFIG_VAR'}") == {'is_set': True}

    os.environ['MY_BOOL_CONFIG_VAR'] = 'false'
    assert loads("{is_set = '$MY_BOOL_CONFIG_VAR'}") == {'is_set': False}


def test_complex_replacement():
    os.environ['MY_LAPTOP_NAME'] = 'laptop'
    os.environ['MY_LAPTOP_PRICE'] = '1000'
    os.environ['MY_IS_LAPTOP_SOLD'] = 'true'

    assert load(open('./tests/test_complex_replacement.toml')) == MORE_COMPLEX_OUTPUT # noqa


def test_loads_with_replace_and_empty_value():
    assert loads("{x = 5, y = '$NON_EXISTENT_VAR'}") == {'x': 5, 'y': ''}


def test_loads_with_replace_dict():
    os.environ['MY_CONFIG_VAR'] = "{z = 123}"
    assert loads("{x = 5, y = '$MY_CONFIG_VAR'}") == {'x': 5, 'y': {'z': 123}}
