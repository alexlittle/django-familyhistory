from django.core.management.base import BaseCommand

from django.utils.translation import gettext, gettext_lazy as _

from familyhistory.models import Person

class Command(BaseCommand):
    help = _("Report for missing data")

    def handle(self, *args, **options):

        # find missing birthdates
        self.missing_birth_dates()

        # is_deceased not set

        # missing death dates

        # missing photo


    def missing_birth_dates(self):
        self.stdout.write(
            self.style.MIGRATE_HEADING(gettext("Checking missing birth dates")))
        for person in Person.objects.all():
            name = self.style.NOTICE(person.get_display_name())
            if person.birth_year is None:
                self.stdout.write(gettext("%(name)s missing birth year") % {"name": name})
            elif person.birth_is_approximate:
                name = self.style.WARNING(person.get_display_name())
                self.stdout.write( gettext("%(name)s birth year is approximate only") % {"name": name})
