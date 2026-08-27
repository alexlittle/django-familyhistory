from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from familyhistory.models import TreeCache
from tests.familyhistory.views.helpers import make_person

# create_tree() is mocked throughout - it has its own tests in test_tree.py.
# These tests are about the command's own job: which people it selects,
# whether it creates-vs-updates the TreeCache row, and what it reports.
#
# Assumes the command lives at
# familyhistory/management/commands/generate_tree.py - adjust the patch
# targets below if it's somewhere else.


class GenerateTreeCommandTests(TestCase):
    def _call(self, *args, **kwargs):
        out = StringIO()
        call_command("generate_tree", *args, stdout=out, **kwargs)
        return out.getvalue()

    @patch("familyhistory.management.commands.generate_tree.create_tree")
    def test_builds_a_tree_cache_for_a_specific_person(self, mock_create_tree):
        person = make_person(first_name="Ada")
        other = make_person(first_name="Bob")
        mock_create_tree.return_value = [{"id": str(person.id)}]

        self._call(person_id=person.id)

        mock_create_tree.assert_called_once_with(person.id)
        cache = TreeCache.objects.get(person=person)
        self.assertEqual(cache.tree, [{"id": str(person.id)}])
        self.assertFalse(TreeCache.objects.filter(person=other).exists())

    @patch("familyhistory.management.commands.generate_tree.create_tree")
    def test_processes_all_known_people_when_no_person_id_given(self, mock_create_tree):
        known = make_person(first_name="Known", is_unknown=False)
        unknown = make_person(first_name="Unknown", is_unknown=True)
        mock_create_tree.return_value = []

        self._call()

        mock_create_tree.assert_called_once_with(known.id)
        self.assertTrue(TreeCache.objects.filter(person=known).exists())
        self.assertFalse(TreeCache.objects.filter(person=unknown).exists())

    @patch("familyhistory.management.commands.generate_tree.create_tree")
    def test_updates_an_existing_tree_cache_instead_of_duplicating(
        self, mock_create_tree
    ):
        person = make_person()
        existing_cache = TreeCache.objects.create(person=person, tree=[{"id": "stale"}])
        mock_create_tree.return_value = [{"id": "fresh"}]

        self._call(person_id=person.id)

        self.assertEqual(TreeCache.objects.filter(person=person).count(), 1)
        existing_cache.refresh_from_db()
        self.assertEqual(existing_cache.tree, [{"id": "fresh"}])

    @patch("familyhistory.management.commands.generate_tree.create_tree")
    def test_writes_a_progress_message_per_person(self, mock_create_tree):
        person = make_person(first_name="Ada", birth_surname="Lovelace")
        mock_create_tree.return_value = []

        output = self._call(person_id=person.id)

        self.assertIn(str(person), output)

    @patch("familyhistory.management.commands.generate_tree.create_tree")
    def test_unknown_person_id_processes_nobody(self, mock_create_tree):
        self._call(person_id=999999)

        mock_create_tree.assert_not_called()
        self.assertEqual(TreeCache.objects.count(), 0)

    @patch("familyhistory.management.commands.generate_tree.create_tree")
    def test_person_id_can_be_passed_as_a_cli_string(self, mock_create_tree):
        # Mirrors real command-line usage (`./manage.py generate_tree -p 5`),
        # where the value arrives as a string. call_command(person_id=5)
        # with an int kwarg skips argparse's parsing entirely, so this
        # checks the ORM filter tolerates the string form too.
        person = make_person()
        mock_create_tree.return_value = []

        self._call("--person_id", str(person.id))

        mock_create_tree.assert_called_once_with(person.id)
        self.assertTrue(TreeCache.objects.filter(person=person).exists())
