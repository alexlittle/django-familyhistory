from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.db.models import Q
from django.urls import reverse_lazy

from .models import Person, Relationship
from .forms import PersonSearchForm, RelationshipForm


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


class SearchPageView(TemplateView):
    template_name = 'fh/search.html'

    def get_context_data(self, **kwargs):
        context = super(SearchPageView, self).get_context_data(**kwargs)
        context['searchform'] = PersonSearchForm(self.request.GET or None)
        return context


class AddRelationshipView(CreateView):
    model = Relationship
    form_class = RelationshipForm
    template_name = 'fh/forms/add_relationship.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['person_id'] = self.kwargs['person_id']
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        initial['person'] = self.kwargs['person_id']
        initial['type'] = self.request.GET.get('type', '')
        return initial

    def form_valid(self, form):
        form.instance.person_id = self.kwargs['person_id']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('fh:person_detail', kwargs={'person_id': self.kwargs['person_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['person'] = Person.objects.get(id=self.kwargs['person_id'])
        context['relationship_type'] = self.request.GET.get('type', '')
        return context



