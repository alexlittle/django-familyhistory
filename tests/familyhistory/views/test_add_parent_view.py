from django.http import HttpResponseRedirect
from django.test import RequestFactory, TestCase
from django.urls import reverse

from familyhistory.models import Person, Relationship
from familyhistory.views import AddParentView
from tests.familyhistory.views.helpers import FakeForm, make_person


class AddParentViewGetTests(TestCase):
    """
    These hit the view through the real URL/form machinery, so they
    depend on ParentForm accepting a related_person_id kwarg - see the
    forms.py note in test_add_relationship_view.py.
    """

    def test_renders_with_expected_template(self):
        child = make_person()

        response = self.client.get(
            reverse("fh:add_parent", kwargs={"related_person_id": child.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "fh/forms/add_parent.html")

    def test_context_includes_the_related_person(self):
        child = make_person(first_name="Child")

        response = self.client.get(
            reverse("fh:add_parent", kwargs={"related_person_id": child.id})
        )

        self.assertEqual(response.context["related_person"], child)

    def test_relationship_type_defaults_to_empty_string(self):
        child = make_person()

        response = self.client.get(
            reverse("fh:add_parent", kwargs={"related_person_id": child.id})
        )

        self.assertEqual(response.context["relationship_type"], "")

    def test_relationship_type_is_read_from_query_string(self):
        child = make_person()

        response = self.client.get(
            reverse("fh:add_parent", kwargs={"related_person_id": child.id}),
            {"type": "is_father_of"},
        )

        self.assertEqual(response.context["relationship_type"], "is_father_of")

    def test_unknown_related_person_id_raises_does_not_exist(self):
        # Same currently-unhandled DoesNotExist as AddRelationshipView -
        # see the note in test_add_relationship_view.py.
        with self.assertRaises(Person.DoesNotExist):
            self.client.get(
                reverse("fh:add_parent", kwargs={"related_person_id": 999999})
            )


class AddParentViewLogicTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.child = make_person(first_name="Child")
        self.parent = make_person(first_name="Parent")

    def _view_for(self, related_person_id):
        request = self.factory.get(f"/fh/person/{related_person_id}/add-parent/")
        view = AddParentView()
        view.setup(request, related_person_id=related_person_id)
        return view

    def test_get_form_kwargs_includes_related_person_id(self):
        view = self._view_for(self.child.id)
        kwargs = view.get_form_kwargs()
        self.assertEqual(kwargs["related_person_id"], self.child.id)

    def test_get_initial_sets_related_person_and_type(self):
        request = self.factory.get(
            f"/fh/person/{self.child.id}/add-parent/",
            {"type": "is_father_of"},
        )
        view = AddParentView()
        view.setup(request, related_person_id=self.child.id)

        initial = view.get_initial()

        self.assertEqual(initial["related_person"], self.child.id)
        self.assertEqual(initial["type"], "is_father_of")

    def test_form_valid_stamps_related_person_id_and_saves(self):
        view = self._view_for(self.child.id)
        instance = Relationship(person=self.parent, type="is_father_of")
        form = FakeForm(instance)

        response = view.form_valid(form)

        self.assertIsInstance(response, HttpResponseRedirect)
        saved = Relationship.objects.get(person=self.parent)
        self.assertEqual(saved.related_person_id, self.child.id)

    def test_get_success_url_points_to_the_related_persons_detail_page(self):
        view = self._view_for(self.child.id)
        self.assertEqual(
            view.get_success_url(),
            reverse("fh:person_detail", kwargs={"person_id": self.child.id}),
        )
