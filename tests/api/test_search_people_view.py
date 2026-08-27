from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory

from api.views import search_people
from familyhistory.models import Person

# Person.search() is mocked throughout: it runs MySQL-specific raw SQL
# (MATCH ... AGAINST), which won't run against a SQLite test database and
# isn't this view's own logic to verify anyway. PersonSerializer is mocked
# too, so these tests aren't coupled to its actual fields.


class SearchPeopleViewTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_returns_empty_list_when_no_query_given(self):
        request = self.factory.get("/fh-data/search/")
        response = search_people(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_blank_query_string_is_treated_as_no_query(self):
        # request.GET.get("q", "") - an explicit ?q= is indistinguishable
        # from a missing one, so it also short-circuits to the empty-list
        # branch without ever calling Person.search().
        with patch.object(Person, "search") as mock_search:
            request = self.factory.get("/fh-data/search/", {"q": ""})
            response = search_people(request)

            mock_search.assert_not_called()
            self.assertEqual(response.data, [])

    @patch("api.views.PersonSerializer")
    @patch.object(Person, "search")
    def test_searches_and_serializes_matching_people(
        self, mock_search, mock_serializer_class
    ):
        mock_search.return_value = ["fake-queryset"]
        mock_serializer_class.return_value.data = [{"id": 1, "label": "Ada Lovelace"}]

        request = self.factory.get("/fh-data/search/", {"q": "Ada"})
        response = search_people(request)

        mock_search.assert_called_once_with("Ada")
        mock_serializer_class.assert_called_once_with(["fake-queryset"], many=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"id": 1, "label": "Ada Lovelace"}])

    def test_post_is_not_allowed(self):
        request = self.factory.post("/fh-data/search/")
        response = search_people(request)
        self.assertEqual(response.status_code, 405)
