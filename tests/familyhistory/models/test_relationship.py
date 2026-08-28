"""Tests for the Relationship model."""

import pytest

from familyhistory.models.person import Person
from familyhistory.models.relationship import Relationship

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_relationship(**kwargs):
    """Unsaved Relationship, for testing pure-Python methods without a DB hit."""
    defaults = {
        "person": Person(first_name="Robert", birth_surname="Smith"),
        "related_person": Person(first_name="Jane", birth_surname="Doe"),
        "type": "is_father_of",
    }
    defaults.update(kwargs)
    return Relationship(**defaults)


# ---------------------------------------------------------------------------
# format_date
# ---------------------------------------------------------------------------


class TestFormatDate:
    def test_start_and_end_present(self):
        relationship = make_relationship(
            start_year=1990, start_month=3, start_day=15, end_year=2000
        )
        assert relationship.format_date() == "15 Mar 1990 - 2000"

    def test_start_only(self):
        relationship = make_relationship(start_year=1990)
        assert relationship.format_date() == "1990"

    def test_neither_returns_placeholder(self):
        assert make_relationship().format_date() == "?"

    def test_end_only_is_dropped(self):
        """format_date only falls back to "?" via the `elif start` branch,
        so an end-only date without a start is not shown."""
        relationship = make_relationship(end_year=2000)
        assert relationship.format_date() == "?"


# ---------------------------------------------------------------------------
# __str__
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestStr:
    def test_str_shows_both_people(self):
        person = Person.objects.create(first_name="Robert", birth_surname="Smith")
        related_person = Person.objects.create(first_name="Jane", birth_surname="Doe")
        relationship = Relationship.objects.create(
            person=person, related_person=related_person, type="is_father_of"
        )
        assert str(relationship) == f"{person} - {related_person}"
