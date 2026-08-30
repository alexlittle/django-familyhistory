"""`manage.py check_document_files`: keep DocumentFile rows and disk files in sync."""

import os

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.urls import reverse
from django.utils.translation import gettext, ngettext
from django.utils.translation import gettext_lazy as _

from familyhistory.models import DocumentFile


def hyperlink(text, url):
    """Wrap text in an OSC 8 terminal hyperlink.

    Args:
        text: The visible link text.
        url: The URL the text should link to.

    Returns:
        The text wrapped in OSC 8 escape sequences.
    """
    return f"\033]8;;{url}\033\\{text}\033]8;;\033\\"


class Command(BaseCommand):
    """Check `DocumentFile` records against files under `MEDIA_ROOT/document/`.

    Reports `DocumentFile` rows whose file is missing on disk, and files on
    disk that no `DocumentFile` row references any more - e.g. left behind
    after a record was deleted, since Django doesn't remove uploaded files
    for you. Pass `--delete-orphans` to remove the latter.
    """

    help = _("Check document files on disk are in sync with DocumentFile records")

    def add_arguments(self, parser):
        """Add the `--delete-orphans` flag.

        Args:
            parser: The argument parser to add options to.
        """
        parser.add_argument(
            "--delete-orphans",
            action="store_true",
            help=_("Delete files on disk that no DocumentFile record references"),
        )

    def handle(self, *args, **options):
        """Run the missing-file and orphaned-file checks.

        Args:
            *args: Unused positional arguments.
            **options: Parsed command options; `delete_orphans` controls
                whether orphaned files found on disk are deleted.
        """
        self.check_missing_files()
        self.check_orphaned_files(delete=options["delete_orphans"])

    def document_file_link(self, document_file):
        """Build a link to the parent document's admin change page for terminal output.

        `DocumentFile` has no standalone admin view - it's only editable
        inline on its `Document` - so this links to the `Document` instead.

        Args:
            document_file: The `DocumentFile` to link to.

        Returns:
            An OSC 8 terminal hyperlink if stdout is a TTY, otherwise a
            plain `"name <url>"` string.
        """
        path = reverse(
            "admin:familyhistory_document_change", args=[document_file.document_id]
        )
        url = f"https://{Site.objects.get_current().domain}{path}"
        name = self.style.NOTICE(str(document_file))
        if not self.stdout.isatty():
            return f"{name} <{url}>"
        return hyperlink(name, url)

    def check_missing_files(self):
        """Report `DocumentFile` rows whose file doesn't exist on disk."""
        self.stdout.write(
            self.style.MIGRATE_HEADING(gettext("Checking for missing document files"))
        )
        counter = 0
        for document_file in DocumentFile.objects.all():
            if not document_file.file.storage.exists(document_file.file.name):
                self.stdout.write(
                    gettext("%(doc)s references a file missing on disk: %(name)s")
                    % {
                        "doc": self.document_file_link(document_file),
                        "name": document_file.file.name,
                    }
                )
                counter += 1
        self.stdout.write(
            self.style.WARNING(
                ngettext(
                    "%(counter)d document file record with a missing file",
                    "%(counter)d document file records with missing files",
                    counter,
                )
                % {"counter": counter}
            )
        )

    def check_orphaned_files(self, delete=False):
        """Report (and optionally delete) files on disk with no matching `DocumentFile` row.

        Only looks under `MEDIA_ROOT/document/`, the upload path used by
        `doc_file_path()`, so it never touches unrelated media such as
        person photos.

        Args:
            delete: If True, delete orphaned files from disk as they're
                found instead of just reporting them.
        """
        self.stdout.write(
            self.style.MIGRATE_HEADING(gettext("Checking for orphaned document files"))
        )

        known_paths = set(DocumentFile.objects.values_list("file", flat=True))

        document_root = os.path.join(settings.MEDIA_ROOT, "document")
        counter = 0
        for dirpath, _dirnames, filenames in os.walk(document_root):
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                relative_path = os.path.relpath(full_path, settings.MEDIA_ROOT).replace(
                    os.sep, "/"
                )

                if relative_path in known_paths:
                    continue

                counter += 1
                if delete:
                    os.remove(full_path)
                    self.stdout.write(
                        gettext("Deleted orphaned file: %(path)s")
                        % {"path": relative_path}
                    )
                else:
                    self.stdout.write(
                        gettext("Orphaned file on disk: %(path)s")
                        % {"path": relative_path}
                    )

        if counter and not delete:
            self.stdout.write(
                self.style.NOTICE(
                    gettext("Re-run with --delete-orphans to remove these files")
                )
            )

        self.stdout.write(
            self.style.WARNING(
                ngettext(
                    "%(counter)d orphaned file found on disk",
                    "%(counter)d orphaned files found on disk",
                    counter,
                )
                % {"counter": counter}
            )
        )
