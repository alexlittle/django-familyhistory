"""Admin configuration for `SiteSetting`."""

from django.contrib import admin

from familyhistory.models import SiteSetting


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    """Admin list/edit view for `SiteSetting` key/value rows."""

    list_display = ("key", "value")
    search_fields = ("key",)
