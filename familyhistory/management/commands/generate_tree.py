import json

from django.core.serializers.json import DjangoJSONEncoder
from django.core.management.base import BaseCommand
from django.db.models import Q

from familyhistory.models import Person, Relationship


class Command(BaseCommand):
    help = "Builds a JSON object of a persons descendants to create the family tree diagram"

    def add_arguments(self, parser):
        parser.add_argument(
            '-p',
            '--person_id',
            dest='person_id',
            required=True,
            help='Person ID to create the tree for',
        )


    def handle(self, *args, **options):
        person_id = options['person_id']  # Access the argument here
        self.stdout.write(f"Generating family tree for person ID: {person_id}")

        root_person = Person.objects.get(id=person_id)
        tree = {
            'id': root_person.id,
            'name': root_person.get_display_name(),
            'children': self.get_children(root_person.id),
            'spouse': self.get_spouse(root_person.id)
        }

        tree_json = json.dumps(tree, cls=DjangoJSONEncoder, indent=4)
        print(tree_json)

    def get_children(self, person_id):
        children = []
        # Find all children
        parent_rels = Relationship.objects.filter(
            person_id=person_id,
            type__in=['is_father_of', 'is_mother_of']
        )
        for rel in parent_rels:
            child = Person.objects.get(id=rel.related_person_id)
            child_node = {
                'id': child.id,
                'name': child.get_display_name(),
                'children': self.get_children(child.id),
                'spouse': self.get_spouse(child.id)  # Check spouse for every child
            }
            children.append(child_node)
        return children

    def get_spouse(self, person_id):
        # Check both directions for spouse/partner
        spouse_rels = Relationship.objects.filter(
            type__in=['is_married_to', 'in_relationship_with']
        ).filter(
            Q(person_id=person_id) | Q(related_person_id=person_id)
        )
        if spouse_rels.exists():
            rel = spouse_rels.first()
            if rel.person_id == person_id:
                spouse = Person.objects.get(id=rel.related_person_id)
            else:
                spouse = Person.objects.get(id=rel.person_id)
            return {
                'id': spouse.id,
                'name': spouse.get_display_name()
            }
        return None