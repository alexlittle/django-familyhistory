"""Tests for the TreeCache model."""

import pytest

from familyhistory.models.person import Person
from familyhistory.models.treecache import TreeCache


@pytest.mark.django_db
class TestStr:
    def test_str_matches_person_str(self):
        person = Person.objects.create(first_name="Robert", birth_surname="Smith")
        tree_cache = TreeCache.objects.create(person=person)
        assert str(tree_cache) == str(person)
