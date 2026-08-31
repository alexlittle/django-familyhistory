"""Tests for the SiteSetting admin."""

from familyhistory.admin.sitesetting import SiteSettingAdmin


def test_list_display_shows_key_and_value():
    assert SiteSettingAdmin.list_display == ("key", "value")


def test_search_fields_includes_key():
    assert SiteSettingAdmin.search_fields == ("key",)
