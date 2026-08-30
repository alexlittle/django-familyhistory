"""Admin configuration for `Document` and `DocumentFile`."""

from typing import ClassVar

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from familyhistory.models import Document, DocumentFile


class DocumentFileInline(admin.TabularInline):
    """Inline editor for a `Document`'s `DocumentFile`s."""

    model = DocumentFile


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin list/edit views for `Document`, with `DocumentFile`s inline."""

    list_display = ("get_display_title", "type", "type_other", "format_doc_date")
    search_fields: ClassVar[list] = ["title", "type", "type_other"]

    def get_display_title(self, obj):
        """Render the document's display title for the change list.

        Args:
            obj: The `Document` being displayed.

        Returns:
            `obj.get_display_title()`.
        """
        return obj.get_display_title()

    get_display_title.short_description = _("Title")
    get_display_title.admin_order_field = "title"

    def format_doc_date(self, obj):
        """Render the document's formatted date for the change list.

        Args:
            obj: The `Document` being displayed.

        Returns:
            The formatted document date.
        """
        return obj.format_doc_date()

    format_doc_date.short_description = _("Date")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "type",
                    "type_other",
                    "description",
                ),
            },
        ),
        (
            _("Date"),
            {
                "fields": (
                    (
                        "doc_year",
                        "doc_month",
                        "doc_day",
                        "doc_date_is_approximate",
                        "doc_date_description",
                    ),
                ),
            },
        ),
        (
            _("People"),
            {
                "fields": ("person_involved",),
                "classes": ("collapse",),
            },
        ),
        (
            _("Events"),
            {
                "fields": ("event_involved",),
                "classes": ("collapse",),
            },
        ),
    )

    # Use filter_horizontal for a user-friendly widget
    filter_horizontal = ("person_involved", "event_involved")

    inlines: ClassVar[list] = [
        DocumentFileInline,
    ]
