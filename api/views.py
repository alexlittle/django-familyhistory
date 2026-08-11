
from django.views import View
from django.http import JsonResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import PersonSerializer

from django.conf import settings
from familyhistory.models import Person
from familyhistory.helpers.tree import create_tree

class FamilyTreeDataView(View):

    def get(self, request, *args, **kwargs):
        start_person_id = self.kwargs.get('start_person_id', settings.TREE_START_PERSON_ID)
        data = create_tree(start_person_id)

        return JsonResponse(data, safe=False)


@api_view(['GET'])
def search_people(request):
    query = request.GET.get('q', '')
    if query:
        people = Person.search(query)
        serializer = PersonSerializer(people, many=True)
        return Response(serializer.data)
    return Response([])