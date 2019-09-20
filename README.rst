envtoml
=======

``envtoml`` is an answer to a fairly simple problem: including values from
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
  DB_PASSWORD=veryToughPa$$w0rd

this config can then be parsed with ``envtoml`` in the following way:


.. code:: python

  from envtoml import load

  cfg = load(open('./config.toml'))

  print(cfg)
  # {'db': {'host': 'some-host.tld',
  #   'port': 3306,
  #   'username': 'user01',
  #   'password': 'veryToughPas$w0rd',
  #   'name': 'my_database'}}

Tests
-----

As this project makes use of `Poetry <https://poetry.eustace.io/>`_, after
installing it the tests can be ran by executing the following from the
project's root directory:

.. code:: bash

    poetry run nosetests tests

They can also be ran with `coverage <https://nose.readthedocs.io/en/latest/plugins/cover.html>`_:

.. code:: bash

    poetry run nosetests --with-coverage tests


License
-------

Licensed under the MIT license (see `LICENSE <./LICENSE>`_ file for more
details).
