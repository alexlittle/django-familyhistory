from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from familyhistory.forms import PersonSearchForm
from familyhistory.models import Person, SiteSetting
from tests.familyhistory.views.helpers import make_person


class HomeViewTests(TestCase):
    def test_renders_with_expected_template(self):
        response = self.client.get(reverse("fh:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "fh/home.html")

    def test_people_are_ordered_by_most_recently_updated(self):
        older = make_person(first_name="Older")
        newer = make_person(first_name="Newer")
        # updated_at has auto_now=True, so Model.save() always overwrites
        # it with "now" - back-date `older` via a queryset .update(),
        # which bypasses auto_now entirely.
        Person.objects.filter(pk=older.pk).update(
            updated_at=timezone.now() - timedelta(days=1)
        )

        response = self.client.get(reverse("fh:home"))

        people = list(response.context["people"])
        self.assertEqual(people[0], newer)
        self.assertIn(older, people)

    def test_context_includes_search_form(self):
        response = self.client.get(reverse("fh:home"))
        self.assertIsInstance(response.context["searchform"], PersonSearchForm)

    def test_pagination_is_20_per_page(self):
        for i in range(21):
            make_person(first_name=f"Person{i}")

        response = self.client.get(reverse("fh:home"))

        self.assertEqual(len(response.context["people"]), 20)
        self.assertTrue(response.context["is_paginated"])

        second_page = self.client.get(reverse("fh:home"), {"page": 2})
        self.assertEqual(len(second_page.context["people"]), 1)

    def test_pagination_size_is_configurable_via_site_setting(self):
        SiteSetting.objects.create(key="homepage_people_count", value="5")
        for i in range(6):
            make_person(first_name=f"Person{i}")

        response = self.client.get(reverse("fh:home"))

        self.assertEqual(len(response.context["people"]), 5)
        self.assertTrue(response.context["is_paginated"])
