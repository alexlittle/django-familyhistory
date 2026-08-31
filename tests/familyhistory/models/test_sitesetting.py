"""Tests for the SiteSetting key/value model."""

import pytest

from familyhistory.models.sitesetting import SiteSetting


@pytest.mark.django_db
class TestGet:
    def test_returns_the_stored_value(self):
        SiteSetting.objects.create(key="homepage_people_count", value="5")

        assert SiteSetting.get("homepage_people_count") == "5"

    def test_returns_default_when_the_key_does_not_exist(self):
        assert SiteSetting.get("missing_key", default="fallback") == "fallback"

    def test_returns_default_when_the_stored_value_is_blank(self):
        SiteSetting.objects.create(key="tree_start_person_id", value="")

        assert SiteSetting.get("tree_start_person_id", default="fallback") == (
            "fallback"
        )

    def test_default_is_none_when_not_given(self):
        assert SiteSetting.get("missing_key") is None


@pytest.mark.django_db
class TestStr:
    def test_str_is_the_key(self):
        setting = SiteSetting.objects.create(key="homepage_people_count", value="20")

        assert str(setting) == "homepage_people_count"
