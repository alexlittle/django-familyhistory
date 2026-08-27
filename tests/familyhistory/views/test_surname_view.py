from django.test import RequestFactory, TestCase
from django.urls import reverse

from familyhistory.models import Person
from familyhistory.views import SurnameView
from tests.familyhistory.views.helpers import make_person


class SurnameViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_matches_birth_surname_case_insensitively(self):
        match = make_person(birth_surname="Smith")
        make_person(birth_surname="Jones")

        response = self.client.get(
            reverse("fh:surname_detail", kwargs={"surname": "smith"})
        )

        self.assertEqual(list(response.context["people"]), [match])

    def test_matches_second_surname(self):
        match = make_person(birth_surname="Lee", second_surname="Smith")

        response = self.client.get(
            reverse("fh:surname_detail", kwargs={"surname": "Smith"})
        )

        self.assertIn(match, response.context["people"])

    def test_matches_current_surname(self):
        match = make_person(birth_surname="Lee", current_surname="Smith")

        response = self.client.get(
            reverse("fh:surname_detail", kwargs={"surname": "Smith"})
        )

        self.assertIn(match, response.context["people"])

    def test_matches_other_surnames_list(self):
        match = make_person(birth_surname="Lee", other_surnames=["Smith", "Brown"])

        response = self.client.get(
            reverse("fh:surname_detail", kwargs={"surname": "Smith"})
        )

        self.assertIn(match, response.context["people"])

    def test_context_includes_the_requested_surname(self):
        response = self.client.get(
            reverse("fh:surname_detail", kwargs={"surname": "Smith"})
        )
        self.assertEqual(response.context["surname"], "Smith")

    def test_results_are_ordered_by_birth_date(self):
        younger = make_person(birth_surname="Smith", birth_year=1990)
        older = make_person(birth_surname="Smith", birth_year=1950)

        response = self.client.get(
            reverse("fh:surname_detail", kwargs={"surname": "Smith"})
        )

        self.assertEqual(list(response.context["people"]), [older, younger])

    def test_get_queryset_without_a_surname_falls_back_to_all_people(self):
        # The URL pattern (surname/<str:surname>) always supplies a
        # non-empty surname, so the "else" branch in get_queryset() isn't
        # reachable through a normal request. Calling the view directly
        # keeps it covered - but it's also worth knowing this branch is
        # effectively dead code given the current URL config.
        make_person(first_name="A")
        make_person(first_name="B")

        request = self.factory.get("/fh/surname/")
        view = SurnameView()
        view.setup(request)

        queryset = view.get_queryset()

        self.assertEqual(
            list(queryset), list(Person.objects.all().order_by("-updated_at"))
        )
