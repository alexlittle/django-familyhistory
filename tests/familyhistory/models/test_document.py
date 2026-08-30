"""Tests for the Document and DocumentFile models."""

import os

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

from familyhistory.models.document import Document, DocumentFile, doc_file_path
from tests.familyhistory.views.helpers import make_person


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

    @pytest.mark.django_db
    def test_str_falls_back_like_get_display_title(self):
        document = create_document(title="", type="birth_certificate")
        assert str(document) == document.get_display_title()


class TestGetDocType:
    def test_uses_type_other_when_set(self):
        document = Document(type="other", type_other="Passenger manifest")
        assert document.get_doc_type() == "Passenger manifest"

    def test_falls_back_to_type_display(self):
        document = Document(type="birth_certificate")
        assert document.get_doc_type() == document.get_type_display()


class TestGetDisplayTitle:
    def test_returns_title_when_set(self):
        document = Document(title="Marriage certificate", type="marriage_certificate")
        assert document.get_display_title() == "Marriage certificate"

    @pytest.mark.django_db
    def test_falls_back_to_doc_type_when_no_title_and_no_people(self):
        document = create_document(title="", type="birth_certificate")
        assert document.get_display_title() == document.get_doc_type()

    @pytest.mark.django_db
    def test_falls_back_to_person_and_doc_type_when_no_title(self):
        document = create_document(title="", type="birth_certificate")
        person = make_person(first_name="Ada", birth_surname="Lovelace")
        document.person_involved.add(person)

        assert document.get_display_title() == (
            f"{person.get_display_name()} - {document.get_doc_type()}"
        )

    @pytest.mark.django_db
    def test_joins_multiple_people_with_a_comma(self):
        document = create_document(title="", type="birth_certificate")
        ada = make_person(first_name="Ada", birth_surname="Lovelace")
        bob = make_person(first_name="Bob", birth_surname="Smith")
        document.person_involved.add(ada, bob)

        assert document.get_display_title() == (
            f"{ada.get_display_name()}, {bob.get_display_name()} - "
            f"{document.get_doc_type()}"
        )


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


# ---------------------------------------------------------------------------
# delete_document_file_from_disk signal
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestDeleteDocumentFileFromDiskSignal:
    def test_deleting_a_document_file_removes_it_from_disk(self, tmp_path):
        with override_settings(MEDIA_ROOT=tmp_path):
            document_file = DocumentFile.objects.create(
                document=create_document(),
                file=SimpleUploadedFile("scan.pdf", b"content"),
            )
            file_path = document_file.file.path
            assert os.path.exists(file_path)

            document_file.delete()

            assert not os.path.exists(file_path)

    def test_deleting_the_parent_document_also_removes_the_file(self, tmp_path):
        with override_settings(MEDIA_ROOT=tmp_path):
            document = create_document()
            document_file = DocumentFile.objects.create(
                document=document,
                file=SimpleUploadedFile("scan.pdf", b"content"),
            )
            file_path = document_file.file.path

            document.delete()

            assert not os.path.exists(file_path)
