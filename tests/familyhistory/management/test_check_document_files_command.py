"""Tests for the "check document files" management command.

These tests require:
  - django.contrib.sites in INSTALLED_APPS with SITE_ID set
  - the admin URLs routed, since document_file_link() reverses
    admin:familyhistory_document_change
"""

import os
from io import StringIO

import pytest
from django.contrib.sites.models import Site
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import override_settings
from django.utils import translation

from familyhistory.management.commands.check_document_files import Command
from familyhistory.models import Document, DocumentFile

COMMAND_NAME = "check_document_files"


@pytest.fixture(autouse=True)
def english():
    """Pin the language so assertions on translated strings are stable."""
    with translation.override("en"):
        yield


@pytest.fixture
def site(db):
    Site.objects.clear_cache()
    current = Site.objects.get_current()
    current.domain = "family.example.com"
    current.save()
    Site.objects.clear_cache()
    yield current
    Site.objects.clear_cache()


@pytest.fixture
def media_root(tmp_path):
    with override_settings(MEDIA_ROOT=tmp_path):
        yield tmp_path


def create_document(**kwargs):
    defaults = {"title": "Birth certificate", "type": "birth_certificate"}
    defaults.update(kwargs)
    return Document.objects.create(**defaults)


def create_document_file(filename="scan.pdf", **kwargs):
    defaults = {"document": create_document()}
    defaults.update(kwargs)
    return DocumentFile.objects.create(
        file=SimpleUploadedFile(filename, b"content"), **defaults
    )


def run_command(**options):
    out = StringIO()
    call_command(COMMAND_NAME, stdout=out, **options)
    return out.getvalue()


# ---------------------------------------------------------------------------
# check_missing_files
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCheckMissingFiles:
    def test_reports_nothing_when_all_files_present(self, media_root, site):
        create_document_file()

        output = run_command()

        assert "0 document file records with missing files" in output

    def test_reports_a_record_whose_file_is_missing_on_disk(self, media_root, site):
        document_file = create_document_file(filename="missing.pdf")
        os.remove(document_file.file.path)

        output = run_command()

        assert "references a file missing on disk" in output
        assert document_file.file.name in output
        assert f"/{document_file.document_id}/" in output
        assert "1 document file record with a missing file" in output

    def test_does_not_flag_a_record_with_no_documentfile_at_all(self, media_root, site):
        # sanity check: an empty DB is not itself "missing files"
        output = run_command()

        assert "0 document file records with missing files" in output


# ---------------------------------------------------------------------------
# check_orphaned_files
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCheckOrphanedFiles:
    def test_reports_nothing_when_no_orphans(self, media_root, site):
        create_document_file()

        output = run_command()

        assert "0 orphaned files found on disk" in output
        assert "Orphaned file on disk" not in output

    def test_reports_a_file_on_disk_with_no_matching_record(self, media_root, site):
        # Mirrors deleting a duplicate DocumentFile record by hand and the
        # underlying file being left behind on disk.
        document_file = create_document_file(filename="duplicate.pdf")
        orphan_dir = media_root / "document" / "birth_certificate"
        orphan_path = orphan_dir / "leftover.pdf"
        orphan_path.write_bytes(b"leftover")

        output = run_command()

        orphan_lines = [
            line
            for line in output.splitlines()
            if line.startswith("Orphaned file on disk")
        ]
        assert len(orphan_lines) == 1
        assert "leftover.pdf" in orphan_lines[0]
        assert document_file.file.name not in orphan_lines[0]
        assert "1 orphaned file found on disk" in output
        assert orphan_path.exists()

    def test_does_not_touch_files_outside_the_document_tree(self, media_root, site):
        other_media = media_root / "photos"
        other_media.mkdir()
        (other_media / "person.jpg").write_bytes(b"photo")

        output = run_command()

        assert "0 orphaned files found on disk" in output
        assert (other_media / "person.jpg").exists()

    def test_delete_orphans_removes_the_file(self, media_root, site):
        orphan_dir = media_root / "document" / "birth_certificate"
        orphan_dir.mkdir(parents=True)
        orphan_path = orphan_dir / "leftover.pdf"
        orphan_path.write_bytes(b"leftover")

        output = run_command(delete_orphans=True)

        assert "Deleted orphaned file" in output
        assert not orphan_path.exists()

    def test_dry_run_leaves_the_file_in_place(self, media_root, site):
        orphan_dir = media_root / "document" / "birth_certificate"
        orphan_dir.mkdir(parents=True)
        orphan_path = orphan_dir / "leftover.pdf"
        orphan_path.write_bytes(b"leftover")

        output = run_command()

        assert "Re-run with --delete-orphans" in output
        assert orphan_path.exists()

    def test_handles_a_missing_document_root_gracefully(self, media_root, site):
        output = run_command()

        assert "0 orphaned files found on disk" in output


# ---------------------------------------------------------------------------
# document_file_link
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestDocumentFileLink:
    def test_non_tty_output_shows_bare_url(self, media_root, site):
        document_file = create_document_file()
        command = Command(stdout=StringIO(), no_color=True)

        result = command.document_file_link(document_file)

        assert "https://family.example.com" in result
        assert f"/{document_file.document_id}/" in result
