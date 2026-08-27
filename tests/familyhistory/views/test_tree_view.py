from django.test import TestCase
from django.urls import reverse

from tests.familyhistory.views.helpers import make_person


class TreeViewTests(TestCase):
    def test_renders_without_a_start_person(self):
        response = self.client.get(reverse("fh:tree"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "fh/tree.html")

    def test_renders_with_a_start_person(self):
        person = make_person()

        response = self.client.get(
            reverse("fh:tree_person", kwargs={"start_person_id": person.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "fh/tree.html")

    def test_renders_even_if_the_start_person_id_does_not_exist(self):
        # TreeView is a plain TemplateView - it doesn't look the person up
        # server-side (presumably the tree data itself comes from a
        # separate API/data view), so an unknown id shouldn't 404 here.
        response = self.client.get(
            reverse("fh:tree_person", kwargs={"start_person_id": 999999})
        )
        self.assertEqual(response.status_code, 200)
