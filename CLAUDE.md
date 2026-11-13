# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A personal Django web app for recording family history: people, relationships, life events,
and documents, plus an auto-generated interactive family tree rendered client-side with
[family-chart.js](https://github.com/donatso/family-chart).

## Commands

Dependencies and the venv are managed with `uv`; the pinned Python version is in `.python-version`.

```bash
uv sync --group dev          # install/update dependencies (dev group: pytest, ruff via pre-commit, etc.)

make run                     # runserver_plus over HTTPS using certs/ (django-extensions, "local" uv group)
make test                    # pytest
make cov                     # pytest --cov --cov-report=term-missing

uv run pytest                                  # full suite
uv run pytest path/to/test_file.py::TestName   # single test/class/module
uv run pytest -k "some_expression"             # filter by name

uvx ruff@0.16.4 check .                        # lint (ruff isn't a project dependency; pre-commit pins v0.16.4)
uvx ruff@0.16.4 format .                       # format

python manage.py makemigrations --check --dry-run   # verify no missing migrations
python manage.py check --deploy                     # Django's deployment security checklist
```

Tests use `DJANGO_SETTINGS_MODULE=settings.ci` (set in `pyproject.toml`
`[tool.pytest.ini_options]` and in `.github/workflows/workflow.yml`), which connects to
MySQL using `DB_NAME`/`DB_USER`/`DB_PASSWORD`/`DB_HOST`/`DB_PORT` env vars (defaults to
root@127.0.0.1:3306, database `familyhistory`). `manage.py` defaults to `settings.dev`.

## Architecture

**Settings** (`settings/` package, which is also the Django project package — it holds
`urls.py` and `wsgi.py` too): `settings/base.py` has the shared config. Each environment
has a module that does `from settings.base import *` and adds its own `SECRET_KEY`,
`DATABASES`, `DEBUG` and `ALLOWED_HOSTS`:
- `settings.dev` — local development (the `manage.py` default). Gitignored.
- `settings.live` — production. Gitignored.
- `settings.ci` — tests and GitHub Actions (MySQL via env vars, throwaway secret key).
- `settings.docs` — Sphinx/Read the Docs build only (in-memory SQLite, throwaway key).

Because `settings.base` is shared with `settings.ci` and so the test client, don't add
settings there that assume real HTTPS traffic (e.g. `SECURE_SSL_REDIRECT`) — the Django
test client makes plain HTTP requests and that would break the suite. Deployment-only
settings like that belong in `settings/live.py` instead.

**Three Django apps**:
- `familyhistory` — the models, server-rendered views/templates, forms, admin, and management
  commands. This is where the actual data model lives.
- `api` — a thin DRF layer (`api/views.py`, `api/serializers.py`) that exposes JSON for the
  browser-side family tree widget and the live person-search box. Not a general-purpose API.
- `settings` — Django project package (per-environment settings modules, root URLconf, WSGI).

**Models** (`familyhistory/models/`, all re-exported from `models/__init__.py`):
- `Person` — the core entity. Names are split into several optional fields
  (`first_name`, `birth_surname`, `current_surname`, `other_surnames` JSON list, etc.)
  because historical records rarely agree on a single "full name". Life/death dates are
  stored as separate nullable year/month/day fields with an `_is_approximate` flag rather
  than a single `DateField`, since genealogical dates are often partial or uncertain
  (`format_partial_date()` in `models/utils.py` renders these consistently, e.g. "c. Mar 1892").
- `Relationship` — directed edges between two `Person`s (`person` → `related_person`) typed
  via `RELATIONSHIP_CHOICES` (parent/child and partner types). Family-tree structure is
  derived entirely from these edges, not stored as a tree.
- `Event`, `Document`/`DocumentFile` — life events and attached documents/files, both linkable
  to one or more `Person`s. `DocumentFile.file` is extension-restricted to images/PDF/office
  formats via `FileExtensionValidator` against `ALLOWED_DOCUMENT_FILE_EXTENSIONS`.
- `TreeCache` — a per-`Person` JSON cache of that person's rendered tree (see below).
- `DateRangeModel` (`models/mixins.py`) — abstract base providing the shared
  start/end partial-date fields used by `Relationship` (e.g. marriage date ranges).
- `SiteSetting` — a generic key/value row (`key`, `value`, both `CharField`) for
  admin-editable config that would otherwise be hardcoded, e.g. the tree's default start
  person (`tree_start_person_id`) and the homepage page size (`homepage_people_count`). New
  settings are added as new rows from the admin, no migration needed. `SiteSetting.get(key,
  default=...)` returns the raw string value (or `default` if the key is missing/blank);
  `familyhistory/helpers/settings.py` defines the well-known keys and wraps them in typed
  getters (`get_tree_start_person_id()`, `get_homepage_people_count()`) — add a new getter
  there, not a Django setting, for values that should be DB-editable rather than code
  constants.

**Tree generation** (`familyhistory/helpers/tree.py`): `create_tree(start_person_id)` loads
all people and parent/partner relationships in bulk, builds in-memory parent/children/partner
lookup maps, and emits a list of node dicts in the shape family-chart.js expects
(`id`, `data`, `rels.{father,mother,spouses,children}`). This is the single source of truth
for tree structure — both the live API endpoint and the cache-generation management command
call it.
- `api/views.FamilyTreeDataView` calls `create_tree()` live, per request.
- `manage.py generate_tree [-p PERSON_ID]` precomputes trees for every non-unknown `Person`
  (or one specific person) and stores them on `TreeCache.tree`, for cases where recomputing
  live is too slow. Nothing currently reads from `TreeCache` automatically — check whether a
  view/consumer has been wired up before assuming the cache is live.

**URL layout**: `settings/urls.py` mounts `familyhistory.urls` (namespace `fh`, server-rendered
pages: home, person detail, tree, search, surname listing, add-relationship/add-parent forms)
and `api.urls` (namespace `fh_data`, JSON endpoints under `/api/`) at the root and `/api/`
respectively.

**Settings unique to this project**: none currently — admin-editable, environment-independent
config like the tree's default start person lives in `SiteSettings` instead (see above), not
in the settings modules.

## Code quality tooling

`pyproject.toml` configures `ruff` (migrations excluded), `interrogate` (docstring coverage)
and `pydoclint` (Google-style docstring/signature consistency) — both run in CI as
non-blocking (`continue-on-error: true`) reports, not gates. Coverage config excludes
migrations, tests, settings files, and `manage.py`.
