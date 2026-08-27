from django.test import TestCase
from django.urls import reverse

from familyhistory.forms import PersonSearchForm


class SearchPageViewTests(TestCase):
    def test_renders_with_expected_template(self):
        response = self.client.get(reverse("fh:person_search"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "fh/search.html")

    def test_context_includes_search_form(self):
        response = self.client.get(reverse("fh:person_search"))
        self.assertIsInstance(response.context["searchform"], PersonSearchForm)

    def test_search_form_is_bound_when_query_params_present(self):
        response = self.client.get(reverse("fh:person_search"), {"q": "smith"})
        self.assertTrue(response.context["searchform"].is_bound)

    def test_search_form_is_unbound_with_no_query_params(self):
        response = self.client.get(reverse("fh:person_search"))
        self.assertFalse(response.context["searchform"].is_bound)
