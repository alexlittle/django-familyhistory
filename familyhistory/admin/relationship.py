"""Admin configuration for `Relationship`."""

from typing import ClassVar

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from familyhistory.models import Relationship


@admin.register(Relationship)
class RelationshipAdmin(admin.ModelAdmin):
    """Admin list/edit views for `Relationship`."""

    list_display = ("person", "type", "related_person", "format_date")
    search_fields: ClassVar[list] = [
        "person__first_name",
        "person__middle_name",
        "person__birth_surname",
        "person__second_surname",
        "person__current_surname",
        "person__known_as",
        "related_person__first_name",
        "related_person__middle_name",
        "related_person__birth_surname",
        "related_person__second_surname",
        "related_person__current_surname",
        "related_person__known_as",
    ]

    def format_date(self, obj):
        """Render the relationship's formatted date range for the change list.

        Args:
            obj: The `Relationship` being displayed.

        Returns:
            The formatted date range.
        """
        return obj.format_date()

    format_date.short_description = _("Dates")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "person",
                    "type",
                    "related_person",
                ),
            },
        ),
        (
            _("Start Date"),
            {
                "fields": (
                    (
                        "start_year",
                        "start_month",
                        "start_day",
                        "start_date_is_approximate",
                        "start_date_description",
                    ),
                ),
            },
        ),
        (
            _("End Date"),
            {
                "fields": (
                    (
                        "end_year",
                        "end_month",
                        "end_day",
                        "end_date_is_approximate",
                        "end_date_description",
                    ),
                ),
            },
        ),
        (
            _("Description"),
            {
                "fields": ("description",),
                "classes": ("collapse",),
            },
        ),
    )
