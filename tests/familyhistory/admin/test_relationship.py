"""Tests for the Relationship admin's computed list_display column."""

from django.contrib import admin

from familyhistory.admin.relationship import RelationshipAdmin
from familyhistory.models.person import Person
from familyhistory.models.relationship import Relationship


def test_format_date_delegates_to_model_method():
    relationship = Relationship(
        person=Person(first_name="Robert", birth_surname="Smith"),
        related_person=Person(first_name="Jane", birth_surname="Doe"),
        type="is_father_of",
        start_year=1990,
    )
    relationship_admin = RelationshipAdmin(Relationship, admin.site)
    assert relationship_admin.format_date(relationship) == relationship.format_date()
