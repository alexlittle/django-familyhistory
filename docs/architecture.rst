Architecture
=============

Apps
-----

The project is split into three Django apps:

- ``familyhistory`` — the models, server-rendered views/templates, forms,
  admin, and management commands. This is where the actual data model
  lives.
- ``api`` — a thin Django REST Framework layer (:mod:`api.views`,
  :mod:`api.serializers`) that exposes JSON for the browser-side family
  tree widget and the live person-search box. It is not a general-purpose
  API.
- ``config`` — Django project configuration (settings, root URLconf, WSGI).

Models
-------

All models live under ``familyhistory/models/`` and are re-exported from
:mod:`familyhistory.models`.

- :class:`~familyhistory.models.person.Person` — the core entity. Names are
  split into several optional fields (``first_name``, ``birth_surname``,
  ``current_surname``, ``other_surnames``, etc.) because historical records
  rarely agree on a single "full name". Life/death dates are stored as
  separate nullable year/month/day fields with an ``_is_approximate`` flag
  rather than a single ``DateField``, since genealogical dates are often
  partial or uncertain — see
  :func:`~familyhistory.models.utils.format_partial_date`.
- :class:`~familyhistory.models.relationship.Relationship` — directed edges
  between two ``Person`` records (``person`` → ``related_person``), typed via
  ``RELATIONSHIP_CHOICES`` (parent/child and partner types). Family-tree
  structure is derived entirely from these edges, not stored as a tree.
- :class:`~familyhistory.models.event.Event` and
  :class:`~familyhistory.models.document.Document` /
  :class:`~familyhistory.models.document.DocumentFile` — life events and
  attached documents/files, both linkable to one or more people.
  ``DocumentFile.file`` is extension-restricted to images/PDF/office formats.
- :class:`~familyhistory.models.treecache.TreeCache` — a per-``Person`` JSON
  cache of that person's rendered tree.
- :class:`~familyhistory.models.mixins.DateRangeModel` — the abstract base
  providing the shared start/end partial-date fields used by
  ``Relationship`` (e.g. marriage date ranges).

Tree generation
-----------------

:func:`familyhistory.helpers.tree.create_tree` loads all people and
parent/partner relationships in bulk, builds in-memory parent/children/partner
lookup maps, and emits the list of node dicts that `family-chart.js
<https://github.com/donatso/family-chart>`_ expects. This is the single
source of truth for tree structure:

- :class:`api.views.FamilyTreeDataView` calls ``create_tree()`` live, per
  request.
- ``manage.py generate_tree [-p PERSON_ID]`` precomputes trees for every
  non-unknown ``Person`` and stores them on ``TreeCache.tree``, for cases
  where recomputing live is too slow. Nothing currently reads from
  ``TreeCache`` automatically.

URL layout
-----------

``config/urls.py`` mounts ``familyhistory.urls`` (namespace ``fh``,
server-rendered pages: home, person detail, tree, search, surname listing,
add-relationship/add-parent forms) and ``api.urls`` (namespace ``fh_data``,
JSON endpoints under ``/api/``) at the root and ``/api/`` respectively.

Settings unique to this project
----------------------------------

``TREE_START_PERSON_ID`` — the default person to root the tree view on.
