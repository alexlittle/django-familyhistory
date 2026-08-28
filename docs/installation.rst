Installation & development
============================

Dependencies and the virtual environment are managed with `uv
<https://docs.astral.sh/uv/>`_; the pinned Python version is in
``.python-version``.

.. code-block:: bash

   uv sync --group dev          # install/update dependencies (pytest, ruff via pre-commit, etc.)

Configuration
--------------

``config/settings.py`` holds the shared/default settings and ends by loading
``config/local_settings.py`` — a gitignored, per-environment override file.
Copy ``config/local_settings_template.py`` to ``config/local_settings.py``
and fill in ``SECRET_KEY``, ``DATABASES``, ``DEBUG`` and ``ALLOWED_HOSTS``
before running the app.

Running the app and tests
---------------------------

.. code-block:: bash

   make run                     # runserver_plus over HTTPS using certs/ (django-extensions)
   make test                    # pytest
   make cov                     # pytest --cov --cov-report=term-missing

   uv run pytest                                  # full suite
   uv run pytest path/to/test_file.py::TestName   # single test/class/module
   uv run pytest -k "some_expression"             # filter by name

Code quality
-------------

.. code-block:: bash

   uvx ruff@0.16.4 check .                        # lint
   uvx ruff@0.16.4 format .                        # format

   python manage.py makemigrations --check --dry-run   # verify no missing migrations
   python manage.py check --deploy                     # Django's deployment security checklist

Building these docs
---------------------

.. code-block:: bash

   uv sync --no-default-groups --group dev
   uv run sphinx-build -b html docs docs/_build/html
