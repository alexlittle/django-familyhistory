from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.urls import reverse
from django.utils.translation import ngettext, gettext, gettext_lazy as _

from familyhistory.models import Person


def hyperlink(text, url):
    """Wrap text in an OSC 8 terminal hyperlink."""
    return f"\033]8;;{url}\033\\{text}\033]8;;\033\\"

class Command(BaseCommand):
    help = _("Report for missing data")

    def handle(self, *args, **options):

        # find missing birthdates
        self.missing_birth_dates()

        # is_deceased not set
        self.is_deceased_not_set()

        # missing death dates
        self.missing_date_of_death()

        # missing photo

    def person_link(self, person):
        path = reverse("admin:familyhistory_person_change", args=[person.pk])
        url = f"https://{Site.objects.get_current().domain}{path}"
        name = self.style.NOTICE(person.get_display_name())
        if not self.stdout.isatty():
            return f"{name} <{url}>"
        return hyperlink(name, url)

    def missing_birth_dates(self):
        """
        Checks for missing or approximate birthdates
        """
        counter_missing = counter_approx = 0
        self.stdout.write(self.style.MIGRATE_HEADING(gettext("Checking missing birth dates")))
        for person in Person.objects.all():
            if person.birth_year is None:
                self.stdout.write(gettext("%(name)s missing birth year") % {"name": self.person_link(person)})
                counter_missing += 1
            elif person.birth_is_approximate:
                self.stdout.write( gettext("%(name)s birth year is approximate only") % {"name": self.person_link(person)})
                counter_approx += 1
        self.stdout.write(self.style.WARNING(
            ngettext(
                "%(counter_missing)d person with no birth year",
                "%(counter_missing)d people with no birth year",
                counter_missing,
            ) % {"counter_missing": counter_missing}))
        self.stdout.write(self.style.WARNING(ngettext(
                "%(counter_approx)d person with approximate birth year",
                "%(counter_approx)d people with approximate birth year",
                counter_approx,
            ) % {"counter_approx": counter_approx}))

    def is_deceased_not_set(self):
        self.stdout.write(self.style.MIGRATE_HEADING(gettext("Checking is_deceased for all persons")))
        counter = 0
        for person in Person.objects.all():
            if person.is_deceased is None:
                self.stdout.write(gettext("is_deceased flag not set for %(name)s") % {"name": self.person_link(person)})
                counter += 1
        self.stdout.write(self.style.WARNING(ngettext(
            "%(counter)d person with is_deceased flag not set",
            "%(counter)d people with is_deceased flag not set",
            counter,
        ) % {"counter": counter}))

    def missing_date_of_death(self):
        """
        Checks for missing or approximate dates of death
        """
        counter_missing = counter_approx = 0
        self.stdout.write(self.style.MIGRATE_HEADING(gettext("Checking missing date of death")))
        for person in Person.objects.all():
            if person.death_year is None and person.is_deceased:
                self.stdout.write(gettext("%(name)s missing year of death") % {"name": self.person_link(person)})
                counter_missing += 1
            elif person.death_is_approximate:
                self.stdout.write( gettext("%(name)s year of death is approximate only") % {"name": self.person_link(person)})
                counter_approx += 1
        self.stdout.write(self.style.WARNING(
            ngettext(
                "%(counter_missing)d person with no year of death",
                "%(counter_missing)d people with no year of death",
                counter_missing,
            ) % {"counter_missing": counter_missing}))
        self.stdout.write(self.style.WARNING(ngettext(
            "%(counter_approx)d person with approximate year of death",
            "%(counter_approx)d people with approximate year of death",
            counter_approx,
        ) % {"counter_approx": counter_approx}))