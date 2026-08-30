"""Tests for the Document admin's computed list_display column."""

from django.contrib import admin

from familyhistory.admin.document import DocumentAdmin
from familyhistory.models.document import Document


def test_format_doc_date_delegates_to_model_method():
    document = Document(doc_year=1990, doc_month=3, doc_day=15)
    document_admin = DocumentAdmin(Document, admin.site)
    assert document_admin.format_doc_date(document) == document.format_doc_date()


def test_get_display_title_delegates_to_model_method():
    document = Document(title="Birth certificate")
    document_admin = DocumentAdmin(Document, admin.site)
    assert document_admin.get_display_title(document) == document.get_display_title()
