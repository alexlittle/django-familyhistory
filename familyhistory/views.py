from django.views.generic import ListView, DetailView

from .models import Person


class HomeView(ListView):
    template_name = 'fh/home.html'
    paginate_by = 20
    context_object_name = 'people'

    def get_queryset(self):
        return Person.objects.all().order_by('-updated_at')


class PersonView(DetailView):
    model = Person
    template_name = 'fh/person.html'
    context_object_name = 'person'
    pk_url_kwarg = 'person_id'

    def get_queryset(self):
        return Person.objects.all().prefetch_related('events_involved')

