"""Admin configuration for `TreeCache`."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from familyhistory.models import TreeCache


@admin.register(TreeCache)
class TreeCacheAdmin(admin.ModelAdmin):
    """Admin list view for `TreeCache`."""

    list_display = ("person_str", "created_at", "updated_at")

    def person_str(self, obj):
        """Render the cache entry's person as a display name for the change list.

        Args:
            obj: The `TreeCache` being displayed.

        Returns:
            The associated person's display name.
        """
        return str(obj.person.get_display_name())

    person_str.short_description = _("Person")
