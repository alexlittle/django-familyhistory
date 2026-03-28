import json

from django.core.serializers.json import DjangoJSONEncoder
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from familyhistory.models import Person, Relationship, TreeCache


class Command(BaseCommand):
    help = _("Builds a JSON object of a persons descendants to create the family tree diagram")

    def add_arguments(self, parser):
        parser.add_argument(
            '-p',
            '--person_id',
            dest='person_id',
            help=_('Person ID to create the tree for')
        )

    def handle(self, *args, **options):

        if options.get('person_id'):
            person_id = options.get('person_id')
            people = Person.objects.filter(id=person_id)
        else:
            people = Person.objects.filter(is_unknown=False)

        for person in people:
            self.stdout.write(_(f"Generating family tree for: {person}"))

            tree_json = None

            tc, created = TreeCache.objects.get_or_create(person=person)
            tc.tree = tree_json
            tc.save()