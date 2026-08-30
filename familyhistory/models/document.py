"""The `Document`/`DocumentFile` models: documents and their attached files."""

import os
from typing import ClassVar

from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import F
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.dates import MONTHS
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField

from .event import Event
from .person import Person
from .utils import (
    ALLOWED_DOCUMENT_FILE_EXTENSIONS,
    DOCUMENT_CHOICES,
    format_partial_date,
)


def doc_file_path(instance, filename):
    """Build the upload path for a `DocumentFile`, grouped by document type.

    Args:
        instance: The `DocumentFile` the file is being uploaded for.
        filename: Original uploaded filename.

    Returns:
        The relative storage path for the file.
    """
    return f"document/{instance.document.type}/{filename}"


class Document(models.Model):
    """A document (certificate, research note, etc.) linked to people and/or events."""

    title = models.CharField(max_length=200, blank=True)
    description = HTMLField(blank=True)
    type = models.CharField(choices=DOCUMENT_CHOICES, max_length=100)
    type_other = models.CharField(max_length=100, blank=True)

    person_involved = models.ManyToManyField(
        Person, related_name="document_people", blank=True
    )
    event_involved = models.ManyToManyField(
        Event, related_name="document_event", blank=True
    )

    doc_year = models.IntegerField(null=True, blank=True)
    doc_month = models.IntegerField(null=True, blank=True, choices=MONTHS)
    doc_day = models.IntegerField(null=True, blank=True)
    doc_date_is_approximate = models.BooleanField(default=False)
    doc_date_description = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Model metadata: display names and default ordering by document date."""

        verbose_name = _("Document")
        verbose_name_plural = _("Documents")
        ordering: ClassVar[list] = [
            F("doc_year").asc(nulls_last=True),
            F("doc_month").asc(nulls_last=True),
            F("doc_day").asc(nulls_last=True),
        ]

    def format_doc_date(self):
        """Format the document's date for display.

        Returns:
            The formatted document date, or `None` if nothing is recorded.
        """
        return format_partial_date(
            self.doc_day, self.doc_month, self.doc_year, self.doc_date_is_approximate
        )

    def __str__(self):
        return self.get_display_title()

    def get_doc_type(self):
        """Human-readable document type, using `type_other` when set.

        Returns:
            `type_other` if the document's type is `"other"` and a custom
            value was given, otherwise the display value of `type`.
        """
        if self.type_other:
            return self.type_other
        else:
            return self.get_type_display()

    def get_display_title(self):
        """Title to show for this document, falling back when none was given.

        `title` is optional - certificates etc. usually don't need one,
        since the people involved and the document type already say what
        it is. Falls back to those instead of showing nothing.

        Returns:
            `title` if set, otherwise "<people involved> - <doc type>" (or
            just the doc type, if no people are linked yet).
        """
        if self.title:
            return self.title

        people = ", ".join(
            person.get_display_name() for person in self.person_involved.all()
        )
        doc_type = self.get_doc_type()
        if people:
            return f"{people} - {doc_type}"
        return doc_type


class DocumentFile(models.Model):
    """A single uploaded file attached to a `Document`.

    A `Document` may have several `DocumentFile`s (e.g. multiple scanned
    pages of the same certificate). `file` is restricted to
    `familyhistory.models.utils.ALLOWED_DOCUMENT_FILE_EXTENSIONS`.
    """

    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="document_file"
    )
    file = models.FileField(
        upload_to=doc_file_path,
        validators=[
            FileExtensionValidator(allowed_extensions=ALLOWED_DOCUMENT_FILE_EXTENSIONS)
        ],
    )
    title = models.CharField(max_length=200, blank=True)

    def __str__(self):
        if self.title:
            return f"{self.document.get_display_title()} {self.title}"
        else:
            return f"{self.document.get_display_title()}"

    class Meta:
        """Model metadata: display names."""

        verbose_name = _("Document File")
        verbose_name_plural = _("Document Files")

    def get_filename(self):
        """Get the file's name without its storage path.

        Returns:
            The base filename.
        """
        return os.path.basename(self.file.name)


@receiver(post_delete, sender=DocumentFile)
def delete_document_file_from_disk(sender, instance, **kwargs):
    """Remove a `DocumentFile`'s underlying file from storage once its row is gone.

    Django never does this on its own, so without this the file is left
    behind on disk both when a `DocumentFile` is deleted directly and when
    its parent `Document` is deleted (cascading to this row).

    Args:
        sender: The model class sending the signal (`DocumentFile`).
        instance: The `DocumentFile` instance that was just deleted.
        **kwargs: Unused signal kwargs.
    """
    instance.file.delete(save=False)
