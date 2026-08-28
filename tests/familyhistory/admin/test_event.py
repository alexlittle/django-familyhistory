"""Tests for the Event admin's computed list_display columns."""

from django.contrib import admin

from familyhistory.admin.event import EventAdmin
from familyhistory.models.event import Event


def test_format_start_date_delegates_to_model_method():
    event = Event(title="Emigrated to Canada", start_year=1990)
    event_admin = EventAdmin(Event, admin.site)
    assert event_admin.format_start_date(event) == event.format_start_date()


def test_format_end_date_delegates_to_model_method():
    event = Event(title="Emigrated to Canada", end_year=1990)
    event_admin = EventAdmin(Event, admin.site)
    assert event_admin.format_end_date(event) == event.format_end_date()
