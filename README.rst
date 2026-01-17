envTOML
=======

.. image:: https://img.shields.io/pypi/v/envtoml.svg
    :target: https://pypi.python.org/pypi/envtoml
    :alt: PyPI Status

.. image:: https://img.shields.io/travis/mrshu/envtoml.svg
    :target: https://travis-ci.org/mrshu/envtoml
    :alt: Build Status

.. image:: https://coveralls.io/repos/github/mrshu/envtoml/badge.svg?branch=master
    :target: https://coveralls.io/github/mrshu/envtoml?branch=master
    :alt: Code coverage Status

.. image:: https://img.shields.io/pypi/l/envtoml.svg
   :target: ./LICENSE
   :alt: License Status

``envTOML`` is an answer to a fairly simple problem: including values from
environment variables in TOML configuration files. In this way, it is very
similar to both `envyaml <https://github.com/thesimj/envyaml>`_ and
`varyaml <https://github.com/abe-winter/varyaml>`_ which provide very
similar functionality for YAML and which greatly inspired this small
package.

Example
-------

Suppose we have the following configuration saved in ``config.toml``

.. code:: toml

  [db]
  host = "$DB_HOST"
  port = "$DB_PORT"
  username = "$DB_USERNAME"
  password = "$DB_PASSWORD"
  name = "my_database"

with the environment variables being set to the following

.. code::

  DB_HOST=some-host.tld
  DB_PORT=3306
  DB_USERNAME=user01
  DB_PASSWORD=veryToughPas$w0rd

this config can then be parsed with ``envTOML`` in the following way:


.. code:: python

  import envtoml

  cfg = envtoml.load(open('./config.toml'))

  print(cfg)
  # {'db': {'host': 'some-host.tld',
  #   'port': 3306,
  #   'username': 'user01',
  #   'password': 'veryToughPas$w0rd',
  #   'name': 'my_database'}}

Tests
-----

This project uses `uv <https://github.com/astral-sh/uv>`_. After installing it,
run the following from the project's root directory:

.. code:: bash

    uv sync --group dev
    uv run pytest

For coverage:

.. code:: bash

    uv run pytest --cov=envtoml


License
-------

Licensed under the MIT license (see `LICENSE <./LICENSE>`_ file for more
details).
