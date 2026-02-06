
from django.views import View
from django.http import JsonResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import PersonSerializer

from django.conf import settings
from familyhistory.models import Person

class FamilyTreeDataView(View):
    """
    {
    "id": "Q508525",
    "data": {
      "fn": "Mary",
      "ln": "Soames",
      "desc": "British aristocrat, daughter of Winston Churchill and his wife Clementine (1922–2014)",
      "label": "Mary Soames",
      "avatar": "https://upload.wikimedia.org/wikipedia/commons/6/69/Mary_Soames_%281965%29.jpg",
      "gender": "F"
    },
    "rels": {
      "father": "Q8016",
      "mother": "Q263454",
      "spouses": [
        "Q336050"
      ],
      "children": [
        "Q390192",
        "Q3052477",
        "Q3453283",
        "Q13408312",
        "Q75386090"
      ]
    },
    "main": false
  },

    """

    def get(self, request, *args, **kwargs):
        data = []
        start_person_id = self.kwargs.get('start_person_id', settings.TREE_START_PERSON_ID)
        people = Person.objects.all()
        for person in people:
            pobj = {}
            pobj['id'] = str(person.id)
            pobj['main'] = True if start_person_id == person.id else False
            pdata = {}
            pdata['fn'] = person.first_name
            pdata['ln'] = person.birth_surname
            pdata['label'] = person.get_display_name()
            pdata['desc'] = f"{person.birth_year} - {person.death_year}"
            pdata['avatar'] = person.photo.url if person.photo else None
            pdata['gender'] = "M" if person.gender == "male" else "F" if person.gender == "female" else None
            pobj['data'] = pdata
            prels = {}
            prels['father'] = str(person.get_parent_id(type="is_father_of") or "")
            prels['mother'] = str(person.get_parent_id(type="is_mother_of") or "")
            prels['spouses'] = person.get_partners(as_id_list=True)
            prels['children'] = person.get_children(as_id_list=True)
            pobj['rels'] = prels
            data.append(pobj)

        return JsonResponse(data, safe=False)


@api_view(['GET'])
def search_people(request):
    query = request.GET.get('q', '')
    if query:
        people = Person.search(query)
        serializer = PersonSerializer(people, many=True)
        return Response(serializer.data)
    return Response([])