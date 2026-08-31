from unittest.mock import patch

from django.test import RequestFactory, SimpleTestCase, TestCase

from api.views import FamilyTreeDataView
from familyhistory.models import SiteSetting
from tests.familyhistory.views.helpers import make_person

# create_tree() is mocked throughout, so these tests don't touch the
# database and don't re-test create_tree's own logic (that lives in
# test_tree.py) - just FamilyTreeDataView's own branching: which
# start_person_id it passes on, and how it wraps the result.


class FamilyTreeDataViewTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("api.views.create_tree")
    def test_uses_start_person_id_from_the_url_kwargs(self, mock_create_tree):
        mock_create_tree.return_value = [{"id": "5"}]

        request = self.factory.get("/fh-data/tree/5")
        FamilyTreeDataView.as_view()(request, start_person_id=5)

        mock_create_tree.assert_called_once_with(5)

    @patch("api.views.create_tree")
    def test_returns_the_tree_data_as_a_json_array(self, mock_create_tree):
        mock_create_tree.return_value = [{"id": "1", "main": True}]

        request = self.factory.get("/fh-data/tree/1")
        response = FamilyTreeDataView.as_view()(request, start_person_id=1)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        # JsonResponse defaults to only allowing dicts unless safe=False -
        # this confirms that flag is actually set, since a regression here
        # would 500 on every request (create_tree returns a list).
        self.assertJSONEqual(response.content, [{"id": "1", "main": True}])

    @patch("api.views.create_tree")
    def test_post_is_not_allowed(self, mock_create_tree):
        request = self.factory.post("/fh-data/tree/1")
        response = FamilyTreeDataView.as_view()(request, start_person_id=1)

        self.assertEqual(response.status_code, 405)
        mock_create_tree.assert_not_called()


class FamilyTreeDataViewSettingsFallbackTests(TestCase):
    # Uses TestCase (not SimpleTestCase) because it hits the database, via
    # SiteSetting.get() and the fallback person.
    def setUp(self):
        self.factory = RequestFactory()

    @patch("api.views.create_tree")
    def test_falls_back_to_site_setting_when_no_start_person_id_given(
        self, mock_create_tree
    ):
        mock_create_tree.return_value = []
        person = make_person()
        SiteSetting.objects.create(key="tree_start_person_id", value=str(person.id))

        request = self.factory.get("/fh-data/tree/")
        FamilyTreeDataView.as_view()(request)

        mock_create_tree.assert_called_once_with(person.id)
