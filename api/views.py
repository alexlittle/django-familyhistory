"""JSON endpoints for the browser-side family tree widget and person-search box."""

from django.conf import settings
from django.http import JsonResponse
from django.views import View
from rest_framework.decorators import api_view
from rest_framework.response import Response

from familyhistory.helpers.tree import create_tree
from familyhistory.models import Person

from .serializers import PersonSerializer


class FamilyTreeDataView(View):
    """Serve the family tree as JSON, computed live via `create_tree`."""

    def get(self, request, *args, **kwargs):
        """Build and return the tree rooted on the requested (or default) person.

        Args:
            request: The current `HttpRequest`.

        Returns:
            A `JsonResponse` containing the list of tree node dicts.
        """
        start_person_id = self.kwargs.get(
            "start_person_id", settings.TREE_START_PERSON_ID
        )
        data = create_tree(start_person_id)

        return JsonResponse(data, safe=False)


@api_view(["GET"])
def search_people(request):
    """Live person-search endpoint backing the search box.

    Args:
        request: The current `HttpRequest`, expecting a `q` query
            parameter with the search text.

    Returns:
        A `Response` with serialized matching `Person`s, or an empty list
        if no query was given.
    """
    query = request.GET.get("q", "")
    if query:
        people = Person.search(query)
        serializer = PersonSerializer(people, many=True)
        return Response(serializer.data)
    return Response([])
