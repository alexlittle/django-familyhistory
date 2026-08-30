Management commands
=====================

All commands live under ``familyhistory/management/commands/`` and are run
the usual Django way:

.. code-block:: bash

   uv run python manage.py <command> [options]

Full docstring-level reference for each command is also available in the
:doc:`API reference <api/management>`.

generate_tree
--------------

Precomputes family trees and stores them on
:class:`~familyhistory.models.treecache.TreeCache`, for cases where
recomputing a tree live (as :class:`api.views.FamilyTreeDataView` normally
does, via :func:`~familyhistory.helpers.tree.create_tree`) is too slow.

.. code-block:: bash

   uv run python manage.py generate_tree                # every non-unknown Person
   uv run python manage.py generate_tree -p PERSON_ID    # just one person

Nothing currently reads from ``TreeCache`` automatically — check whether a
view/consumer has been wired up before assuming the cache is live.

data_report
------------

Reports on :class:`~familyhistory.models.person.Person` records with
missing or approximate data: missing birth dates, an unset ``is_deceased``
flag, and missing death dates for people marked deceased.

.. code-block:: bash

   uv run python manage.py data_report

Each finding is written to stdout as a link to that person's admin change
page — a clickable OSC 8 terminal hyperlink when stdout is a TTY, otherwise
a plain ``name <url>`` line.

check_document_files
----------------------

Checks that :class:`~familyhistory.models.document.DocumentFile` records
and the files actually stored under ``MEDIA_ROOT/document/`` agree with
each other. Django doesn't clean up uploaded files on its own, so this
catches two kinds of drift:

- **Missing files** — a ``DocumentFile`` row whose file no longer exists on
  disk.
- **Orphaned files** — a file on disk with no ``DocumentFile`` row
  referencing it any more, e.g. left behind after a duplicate upload's
  record was deleted by hand.

.. code-block:: bash

   uv run python manage.py check_document_files                  # report only
   uv run python manage.py check_document_files --delete-orphans # also delete orphaned files

Only files under the ``document/`` upload tree are considered, so it never
touches unrelated media such as person photos.
