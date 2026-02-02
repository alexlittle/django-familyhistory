from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.shortcuts import render

from .models import Person
from .forms import PersonSearchForm

class HomeView(ListView):
    template_name = 'fh/home.html'
    paginate_by = 20
    context_object_name = 'people'

    def get_queryset(self):
        return Person.objects.all().order_by('-updated_at')

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['surnames'] = Person.get_surname_counts()
        context['searchform'] = PersonSearchForm(self.request.GET or None)
        return context


class PersonView(DetailView):
    model = Person
    template_name = 'fh/person.html'
    context_object_name = 'person'
    pk_url_kwarg = 'person_id'

    def get_queryset(self):
        return Person.objects.all().prefetch_related('events_involved', 'document_people')


class TreeView(DetailView):
    model = Person
    template_name = 'fh/tree.html'
    context_object_name = 'person'
    pk_url_kwarg = 'person_id'

    def get_queryset(self):
        return Person.objects.all()

class SurnameView(ListView):
    template_name = 'fh/surname.html'
    paginate_by = 20
    context_object_name = 'people'

    def get_context_data(self, **kwargs):
        context = super(SurnameView, self).get_context_data(**kwargs)
        context['surname'] =  self.kwargs.get('surname', None)
        return context

    def get_queryset(self):
        # Get the surname from the URL
        surname = self.kwargs.get('surname', None)

        # If a surname is provided, filter the queryset
        if surname:
            queryset = Person.objects.filter(
                Q(birth_surname__iexact=surname) |
                Q(second_surname__iexact=surname) |
                Q(current_surname__iexact=surname) |
                Q(other_surnames__contains=[surname])
            ).order_by('birth_year', 'birth_month', 'birth_day')
        else:
            # If no surname is provided, return all people
            queryset = Person.objects.all().order_by('-updated_at')

        return queryset


def search_page(request):
    return render(request, 'fh/search.html')