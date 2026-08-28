"""Tests for the TreeCache admin's computed list_display column."""

import pytest
from django.contrib import admin

from familyhistory.admin.treecache import TreeCacheAdmin
from familyhistory.models.person import Person
from familyhistory.models.treecache import TreeCache


@pytest.mark.django_db
def test_person_str_uses_display_name():
    person = Person.objects.create(first_name="Robert", birth_surname="Smith")
    tree_cache = TreeCache.objects.create(person=person)
    tree_cache_admin = TreeCacheAdmin(TreeCache, admin.site)
    assert tree_cache_admin.person_str(tree_cache) == person.get_display_name()


def test_list_display_includes_person_str():
    """Regression test for a typo (`ist_display`) that silently dropped the
    custom columns and fell back to Django's default single-column list."""
    tree_cache_admin = TreeCacheAdmin(TreeCache, admin.site)
    assert tree_cache_admin.list_display == (
        "person_str",
        "created_at",
        "updated_at",
    )
