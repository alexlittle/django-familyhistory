"""`manage.py generate_tree`: precompute and store `TreeCache` entries."""

from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy

from familyhistory.helpers.tree import create_tree
from familyhistory.models import Person, TreeCache


class Command(BaseCommand):
    """Precompute family trees and store them on `TreeCache`.

    Runs `familyhistory.helpers.tree.create_tree` for every non-unknown
    `Person` (or a single person given via `-p`) and saves the result to
    that person's `TreeCache.tree`, for cases where recomputing the tree
    live is too slow.
    """

    help = gettext_lazy(
        "Builds a JSON object of a persons descendants to create the family tree diagram"
    )

    def add_arguments(self, parser):
        """Add the `-p/--person_id` option restricting the command to one person.

        Args:
            parser: The argument parser to add options to.
        """
        parser.add_argument(
            "-p",
            "--person_id",
            dest="person_id",
            help=gettext_lazy("Person ID to create the tree for"),
        )

    def handle(self, *args, **options):
        """Generate and cache the tree for the requested person(s).

        Args:
            *args: Unused positional arguments.
            **options: Parsed command options; `person_id` restricts the
                run to a single person if given.
        """
        if options.get("person_id"):
            person_id = options.get("person_id")
            people = Person.objects.filter(id=person_id)
        else:
            people = Person.objects.filter(is_unknown=False)

        for person in people:
            self.stdout.write(
                gettext_lazy("Generating family tree for: %(person)s")
                % {"person": person}
            )

            tree_json = create_tree(person.id)

            tc, _ = TreeCache.objects.get_or_create(person=person)
            tc.tree = tree_json
            tc.save()
