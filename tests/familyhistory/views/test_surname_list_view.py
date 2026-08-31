from django.test import TestCase
from django.urls import reverse

from tests.familyhistory.views.helpers import make_person


class SurnameListViewTests(TestCase):
    def test_renders_with_expected_template(self):
        response = self.client.get(reverse("fh:surname_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "fh/surnames.html")

    def test_context_includes_surname_counts(self):
        make_person(birth_surname="Smith")
        make_person(birth_surname="Smith")
        make_person(birth_surname="Jones")

        response = self.client.get(reverse("fh:surname_list"))

        self.assertIn(("Jones", 1), response.context["surnames"])
        self.assertIn(("Smith", 2), response.context["surnames"])
