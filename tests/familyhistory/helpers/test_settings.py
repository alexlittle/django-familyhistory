"""Tests for the typed SiteSetting accessors in familyhistory.helpers.settings."""

import pytest

from familyhistory.helpers.settings import (
    DEFAULT_HOMEPAGE_PEOPLE_COUNT,
    get_homepage_people_count,
    get_tree_start_person_id,
)
from familyhistory.models import SiteSetting


@pytest.mark.django_db
class TestGetTreeStartPersonId:
    def test_returns_the_configured_id_as_an_int(self):
        SiteSetting.objects.create(key="tree_start_person_id", value="42")

        assert get_tree_start_person_id() == 42

    def test_returns_none_when_unset(self):
        assert get_tree_start_person_id() is None


@pytest.mark.django_db
class TestGetHomepagePeopleCount:
    def test_returns_the_configured_count_as_an_int(self):
        SiteSetting.objects.create(key="homepage_people_count", value="5")

        assert get_homepage_people_count() == 5

    def test_returns_the_default_when_unset(self):
        assert get_homepage_people_count() == DEFAULT_HOMEPAGE_PEOPLE_COUNT
