"""Tests for the PersonSerializer."""

from api.serializers import PersonSerializer
from familyhistory.models.person import Person


def test_display_name_delegates_to_model_method():
    person = Person(first_name="Robert", birth_surname="Smith")
    data = PersonSerializer(person).data
    assert data["display_name"] == person.get_display_name()


def test_birth_death_date_delegates_to_model_method():
    person = Person(first_name="Robert", birth_surname="Smith", birth_year=1990)
    data = PersonSerializer(person).data
    assert data["birth_death_date"] == person.get_birth_death_date()
