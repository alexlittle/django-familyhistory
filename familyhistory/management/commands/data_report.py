"""`manage.py data_report`: report on people with missing or approximate data."""

from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.urls import reverse
from django.utils.translation import gettext, ngettext
from django.utils.translation import gettext_lazy as _

from familyhistory.models import Person
from familyhistory.models.utils import DECEASED


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
    """Report on `Person` records with missing or approximate data.

    Checks birth dates, the `is_deceased` flag, and death dates, writing
    a summary of gaps to stdout (as clickable terminal hyperlinks when
    stdout is a TTY, otherwise as plain `name <url>` text).
    """

    help = _("Report for missing data")

    def handle(self, *args, **options):
        """Run all the individual data-quality checks in turn.

        Args:
            *args: Unused positional arguments.
            **options: Unused parsed command options.
        """
        # find missing birthdates
        self.missing_birth_dates()

        # is_deceased not set
        self.is_deceased_not_set()

        # missing death dates
        self.missing_date_of_death()

        # missing photo

    def person_link(self, person):
        """Build a link to a person's admin change page for terminal output.

        Args:
            person: The `Person` to link to.

        Returns:
            An OSC 8 terminal hyperlink if stdout is a TTY, otherwise a
            plain `"name <url>"` string.
        """
        path = reverse("admin:familyhistory_person_change", args=[person.pk])
        url = f"https://{Site.objects.get_current().domain}{path}"
        name = self.style.NOTICE(person.get_display_name())
        if not self.stdout.isatty():
            return f"{name} <{url}>"
        return hyperlink(name, url)

    def missing_birth_dates(self):
        """Check for and report on people with missing or approximate birth years."""
        counter_missing = counter_approx = 0
        self.stdout.write(
            self.style.MIGRATE_HEADING(gettext("Checking missing birth dates"))
        )
        for person in Person.objects.all():
            if person.birth_year is None:
                self.stdout.write(
                    gettext("%(name)s missing birth year")
                    % {"name": self.person_link(person)}
                )
                counter_missing += 1
            elif person.birth_is_approximate:
                self.stdout.write(
                    gettext("%(name)s birth year is approximate only")
                    % {"name": self.person_link(person)}
                )
                counter_approx += 1
        self.stdout.write(
            self.style.WARNING(
                ngettext(
                    "%(counter_missing)d person with no birth year",
                    "%(counter_missing)d people with no birth year",
                    counter_missing,
                )
                % {"counter_missing": counter_missing}
            )
        )
        self.stdout.write(
            self.style.WARNING(
                ngettext(
                    "%(counter_approx)d person with approximate birth year",
                    "%(counter_approx)d people with approximate birth year",
                    counter_approx,
                )
                % {"counter_approx": counter_approx}
            )
        )

    def is_deceased_not_set(self):
        """Check for and report on people with no `is_deceased` flag set."""
        self.stdout.write(
            self.style.MIGRATE_HEADING(gettext("Checking is_deceased for all persons"))
        )
        counter = 0
        for person in Person.objects.all():
            if person.is_deceased is None:
                self.stdout.write(
                    gettext("is_deceased flag not set for %(name)s")
                    % {"name": self.person_link(person)}
                )
                counter += 1
        self.stdout.write(
            self.style.WARNING(
                ngettext(
                    "%(counter)d person with is_deceased flag not set",
                    "%(counter)d people with is_deceased flag not set",
                    counter,
                )
                % {"counter": counter}
            )
        )

    def missing_date_of_death(self):
        """Check for and report on deceased people with missing or approximate death years."""
        counter_missing = counter_approx = 0
        self.stdout.write(
            self.style.MIGRATE_HEADING(gettext("Checking missing date of death"))
        )
        for person in Person.objects.all():
            if person.death_year is None and person.death_status == DECEASED:
                self.stdout.write(
                    gettext("%(name)s missing year of death")
                    % {"name": self.person_link(person)}
                )
                counter_missing += 1
            elif person.death_is_approximate:
                self.stdout.write(
                    gettext("%(name)s year of death is approximate only")
                    % {"name": self.person_link(person)}
                )
                counter_approx += 1
        self.stdout.write(
            self.style.WARNING(
                ngettext(
                    "%(counter_missing)d person with no year of death",
                    "%(counter_missing)d people with no year of death",
                    counter_missing,
                )
                % {"counter_missing": counter_missing}
            )
        )
        self.stdout.write(
            self.style.WARNING(
                ngettext(
                    "%(counter_approx)d person with approximate year of death",
                    "%(counter_approx)d people with approximate year of death",
                    counter_approx,
                )
                % {"counter_approx": counter_approx}
            )
        )
