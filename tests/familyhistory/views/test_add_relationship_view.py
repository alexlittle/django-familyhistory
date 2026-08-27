from django.http import HttpResponseRedirect
from django.test import RequestFactory, TestCase
from django.urls import reverse

from familyhistory.models import Person, Relationship
from familyhistory.views import AddRelationshipView
from tests.familyhistory.views.helpers import FakeForm, make_person


class AddRelationshipViewGetTests(TestCase):
    """
    These hit the view through the real URL/form machinery, so they
    depend on RelationshipForm accepting a person_id kwarg - see the
    note at the top of the conversation about forms.py not being
    available. If RelationshipForm doesn't support that, these will
    fail and point you straight at the mismatch.
    """

    def test_renders_with_expected_template(self):
        person = make_person()

        response = self.client.get(
            reverse("fh:add_relationship", kwargs={"person_id": person.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "fh/forms/add_relationship.html")

    def test_context_includes_the_person(self):
        person = make_person(first_name="Ada")

        response = self.client.get(
            reverse("fh:add_relationship", kwargs={"person_id": person.id})
        )

        self.assertEqual(response.context["person"], person)

    def test_relationship_type_defaults_to_empty_string(self):
        person = make_person()

        response = self.client.get(
            reverse("fh:add_relationship", kwargs={"person_id": person.id})
        )

        self.assertEqual(response.context["relationship_type"], "")

    def test_relationship_type_is_read_from_query_string(self):
        person = make_person()

        response = self.client.get(
            reverse("fh:add_relationship", kwargs={"person_id": person.id}),
            {"type": "is_married_to"},
        )

        self.assertEqual(response.context["relationship_type"], "is_married_to")

    def test_unknown_person_id_raises_does_not_exist(self):
        # get_context_data() looks the person up with Person.objects.get()
        # rather than get_object_or_404(), so an unknown id currently
        # surfaces as an unhandled DoesNotExist (500) rather than a 404.
        # This test documents that current behaviour; tighten it to
        # assertEqual(response.status_code, 404) if you switch to
        # get_object_or_404.
        with self.assertRaises(Person.DoesNotExist):
            self.client.get(
                reverse("fh:add_relationship", kwargs={"person_id": 999999})
            )


class AddRelationshipViewLogicTests(TestCase):
    """
    Exercises the view's own overrides directly, using FakeForm so they
    don't depend on RelationshipForm's real fields.
    """

    def setUp(self):
        self.factory = RequestFactory()
        self.person = make_person(first_name="Parent")
        self.related_person = make_person(first_name="Partner")

    def _view_for(self, person_id):
        request = self.factory.get(f"/fh/person/{person_id}/add-relationship/")
        view = AddRelationshipView()
        view.setup(request, person_id=person_id)
        return view

    def test_get_form_kwargs_includes_person_id(self):
        view = self._view_for(self.person.id)
        kwargs = view.get_form_kwargs()
        self.assertEqual(kwargs["person_id"], self.person.id)

    def test_get_initial_sets_person_and_type(self):
        request = self.factory.get(
            f"/fh/person/{self.person.id}/add-relationship/",
            {"type": "is_married_to"},
        )
        view = AddRelationshipView()
        view.setup(request, person_id=self.person.id)

        initial = view.get_initial()

        self.assertEqual(initial["person"], self.person.id)
        self.assertEqual(initial["type"], "is_married_to")

    def test_form_valid_stamps_person_id_and_saves(self):
        view = self._view_for(self.person.id)
        instance = Relationship(
            related_person=self.related_person, type="is_married_to"
        )
        form = FakeForm(instance)

        response = view.form_valid(form)

        self.assertIsInstance(response, HttpResponseRedirect)
        saved = Relationship.objects.get(related_person=self.related_person)
        self.assertEqual(saved.person_id, self.person.id)

    def test_get_success_url_points_to_the_person_detail_page(self):
        view = self._view_for(self.person.id)
        self.assertEqual(
            view.get_success_url(),
            reverse("fh:person_detail", kwargs={"person_id": self.person.id}),
        )
