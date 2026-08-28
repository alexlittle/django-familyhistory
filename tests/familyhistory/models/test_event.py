"""Tests for the Event model."""

from familyhistory.models.event import Event


class TestStr:
    def test_str_returns_title(self):
        assert str(Event(title="Emigrated to Canada")) == "Emigrated to Canada"
