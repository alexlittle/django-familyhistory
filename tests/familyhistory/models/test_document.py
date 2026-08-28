"""Tests for the Document and DocumentFile models."""

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from familyhistory.models.document import Document, DocumentFile, doc_file_path


def create_document(**kwargs):
    """Persisted Document, for attaching DocumentFiles in tests."""
    defaults = {"title": "Birth certificate", "type": "birth_certificate"}
    defaults.update(kwargs)
    return Document.objects.create(**defaults)


# ---------------------------------------------------------------------------
# doc_file_path
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_doc_file_path_uses_document_type():
    document = create_document(type="birth_certificate")
    document_file = DocumentFile(document=document)
    assert (
        doc_file_path(document_file, "scan.pdf")
        == "document/birth_certificate/scan.pdf"
    )


# ---------------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------------


class TestDocumentStr:
    def test_str_returns_title(self):
        assert str(Document(title="Birth certificate")) == "Birth certificate"


class TestGetDocType:
    def test_uses_type_other_when_set(self):
        document = Document(type="other", type_other="Passenger manifest")
        assert document.get_doc_type() == "Passenger manifest"

    def test_falls_back_to_type_display(self):
        document = Document(type="birth_certificate")
        assert document.get_doc_type() == document.get_type_display()


# ---------------------------------------------------------------------------
# DocumentFile
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestDocumentFileStr:
    def test_includes_title_when_set(self):
        document_file = DocumentFile(document=create_document(), title="Front page")
        assert str(document_file) == "Birth certificate Front page"

    def test_falls_back_to_document_title_when_no_title(self):
        document_file = DocumentFile(document=create_document())
        assert str(document_file) == "Birth certificate"


class TestGetFilename:
    def test_returns_basename_of_file_path(self):
        document_file = DocumentFile()
        document_file.file.name = "document/birth_certificate/scan.pdf"
        assert document_file.get_filename() == "scan.pdf"


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
