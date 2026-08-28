"""Tests for the Person admin's computed list_display columns."""

from django.contrib import admin

from familyhistory.admin.person import PersonAdmin
from familyhistory.models.person import Person


def test_format_birth_date_delegates_to_model_method():
    person = Person(first_name="Robert", birth_surname="Smith", birth_year=1990)
    person_admin = PersonAdmin(Person, admin.site)
    assert person_admin.format_birth_date(person) == person.format_birth_date()


def test_format_death_date_delegates_to_model_method():
    person = Person(first_name="Robert", birth_surname="Smith", death_year=1990)
    person_admin = PersonAdmin(Person, admin.site)
    assert person_admin.format_death_date(person) == person.format_death_date()
