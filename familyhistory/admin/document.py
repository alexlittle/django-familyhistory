from typing import ClassVar

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from familyhistory.models import Document, DocumentFile


class DocumentFileInline(admin.TabularInline):
    model = DocumentFile


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "type", "type_other", "format_doc_date")
    search_fields: ClassVar[list] = ["title", "type", "type_other"]

    def format_doc_date(self, obj):
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
