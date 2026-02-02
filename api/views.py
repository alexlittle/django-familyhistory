import json
from django.views import View
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
from familyhistory.models import Person
from .serializers import PersonSerializer
from familyhistory.models import Person

class FamilyTreeDataView(View):
    """
    A class-based view to return family tree data as JSON.
    """

    def get(self, request, *args, **kwargs):

        person_id = kwargs.get('person_id')
        if not person_id:
            return JsonResponse({'error': _('person_id is required')}, status=400)

        try:
            person = Person.objects.get(id=person_id)
        except Person.DoesNotExist:
            return JsonResponse({'error': _('Person not found')}, status=404)

        tree = person.get_tree()
        if tree is None:
            return JsonResponse({'error': _('Tree not found')}, status=404)

        if isinstance(tree, str):
            tree = json.loads(tree)

        return JsonResponse(tree)


@api_view(['GET'])
def search_people(request):
    query = request.GET.get('q', '')
    if query:
        people = Person.search(query)
        serializer = PersonSerializer(people, many=True)
        return Response(serializer.data)
    return Response([])