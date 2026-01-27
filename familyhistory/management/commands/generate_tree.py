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
            'families': self.get_families(root_person.id)
        }
        tree_json = json.dumps(tree, cls=DjangoJSONEncoder, indent=4)
        print(tree_json)

    def get_families(self, person_id):
        families = []
        # Find all spouses
        spouse_rels = Relationship.objects.filter(
            Q(type__in=['is_married_to', 'in_relationship_with']) &
            (Q(person_id=person_id) | Q(related_person_id=person_id))
        )
        for rel in spouse_rels:
            if rel.person_id == person_id:
                spouse_id = rel.related_person_id
            else:
                spouse_id = rel.person_id
            spouse = Person.objects.get(id=spouse_id)
            # Find children with this spouse
            children = []
            child_rels = Relationship.objects.filter(
                Q(type__in=['is_father_of', 'is_mother_of']),
                Q(person_id=person_id)
            )
            for child_rel in child_rels:
                child = Person.objects.get(id=child_rel.related_person_id)
                # Check if the spouse is also a parent of this child
                is_spouse_parent = Relationship.objects.filter(
                    Q(type__in=['is_father_of', 'is_mother_of']),
                    Q(person_id=spouse_id),
                    Q(related_person_id=child.id)
                ).exists()
                if is_spouse_parent:
                    children.append({
                        'id': child.id,
                        'name': child.get_display_name(),
                        'families': self.get_families(child.id)
                    })
            families.append({
                'spouse': {
                    'id': spouse.id,
                    'name': spouse.get_display_name()
                },
                'children': children
            })
        return families