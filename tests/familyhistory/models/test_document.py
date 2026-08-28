"""Tests for the DocumentFile model's file-extension validation."""

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from familyhistory.models.document import Document, DocumentFile


def create_document(**kwargs):
    """Persisted Document, for attaching DocumentFiles in tests."""
    defaults = {"title": "Birth certificate", "type": "birth_certificate"}
    defaults.update(kwargs)
    return Document.objects.create(**defaults)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "filename", ["scan.pdf", "photo.jpg", "notes.txt", "record.docx"]
)
def test_allowed_extensions_pass_validation(filename):
    doc_file = DocumentFile(
        document=create_document(),
        file=SimpleUploadedFile(filename, b"content"),
    )
    doc_file.full_clean()


@pytest.mark.django_db
@pytest.mark.parametrize("filename", ["script.exe", "archive.zip", "payload.sh"])
def test_disallowed_extensions_fail_validation(filename):
    doc_file = DocumentFile(
        document=create_document(),
        file=SimpleUploadedFile(filename, b"content"),
    )
    with pytest.raises(ValidationError):
        doc_file.full_clean()
