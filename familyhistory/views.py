"""Server-rendered pages: home, person detail, tree, search, surname listing, add-relationship/parent forms."""

from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView

from .forms import ParentForm, PersonSearchForm, RelationshipForm
from .models import Person, Relationship


class HomeView(ListView):
    """Home page: recently-updated people, surname counts, and the search box."""

    template_name = "fh/home.html"
    paginate_by = 20
    context_object_name = "people"

    def get_queryset(self):
        """List all people, most recently updated first.

        Returns:
            All `Person`s, most recently updated first.
        """
        return Person.objects.all().order_by("-updated_at")

    def get_context_data(self, **kwargs):
        """Add surname counts and the search form to the template context.

        Returns:
            The template context, with `surnames` and `searchform` added.
        """
        context = super().get_context_data(**kwargs)
        context["surnames"] = Person.get_surname_counts()
        context["searchform"] = PersonSearchForm(self.request.GET or None)
        return context


class PersonView(DetailView):
    """A single person's detail page, including their events and documents."""

    model = Person
    template_name = "fh/person.html"
    context_object_name = "person"
    pk_url_kwarg = "person_id"

    def get_queryset(self):
        """List all people, with related events and documents prefetched.

        Returns:
            All `Person`s, with `events_involved` and `document_people`
            prefetched.
        """
        return Person.objects.all().prefetch_related(
            "events_involved", "document_people"
        )


class TreeView(TemplateView):
    """The interactive family tree page, rendered client-side by family-chart.js."""

    template_name = "fh/tree.html"


class SurnameView(ListView):
    """People sharing a given surname, or all people if none is specified."""

    template_name = "fh/surname.html"
    paginate_by = 20
    context_object_name = "people"

    def get_context_data(self, **kwargs):
        """Add the requested surname to the template context.

        Returns:
            The template context, with the `surname` URL kwarg added.
        """
        context = super().get_context_data(**kwargs)
        context["surname"] = self.kwargs.get("surname", None)
        return context

    def get_queryset(self):
        """List people matching the requested surname.

        Returns:
            `Person`s matching the `surname` URL kwarg across
            `birth_surname`, `second_surname`, `current_surname`, and
            `other_surnames`, or all `Person`s if no surname was given.
        """
        # Get the surname from the URL
        surname = self.kwargs.get("surname", None)

        # If a surname is provided, filter the queryset
        if surname:
            queryset = Person.objects.filter(
                Q(birth_surname__iexact=surname)
                | Q(second_surname__iexact=surname)
                | Q(current_surname__iexact=surname)
                | Q(other_surnames__contains=[surname])
            ).order_by("birth_year", "birth_month", "birth_day")
        else:
            # If no surname is provided, return all people
            queryset = Person.objects.all().order_by("-updated_at")

        return queryset


class SearchPageView(TemplateView):
    """The person-search page, backed by the live-search API."""

    template_name = "fh/search.html"

    def get_context_data(self, **kwargs):
        """Add the search form to the template context.

        Returns:
            The template context, with `searchform` added.
        """
        context = super().get_context_data(**kwargs)
        context["searchform"] = PersonSearchForm(self.request.GET or None)
        return context


class AddRelationshipView(CreateView):
    """Form to add a partner or child relationship from a given person."""

    model = Relationship
    form_class = RelationshipForm
    template_name = "fh/forms/add_relationship.html"

    def get_form_kwargs(self):
        """Pass the source person's ID through to `RelationshipForm`.

        Returns:
            The form kwargs, with `person_id` added.
        """
        kwargs = super().get_form_kwargs()
        kwargs["person_id"] = self.kwargs["person_id"]
        return kwargs

    def get_initial(self):
        """Pre-fill the source person and relationship type.

        Returns:
            The initial form data, with `person` and `type` set.
        """
        initial = super().get_initial()
        initial["person"] = self.kwargs["person_id"]
        initial["type"] = self.request.GET.get("type", "")
        return initial

    def form_valid(self, form):
        """Set `person` from the URL before saving the new relationship.

        Args:
            form: The validated `RelationshipForm`.

        Returns:
            The redirect response from the parent implementation.
        """
        form.instance.person_id = self.kwargs["person_id"]
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect back to the source person's detail page after saving.

        Returns:
            The URL of the source person's detail page.
        """
        return reverse_lazy(
            "fh:person_detail", kwargs={"person_id": self.kwargs["person_id"]}
        )

    def get_context_data(self, **kwargs):
        """Add the source person and requested relationship type to the context.

        Returns:
            The template context, with `person` and `relationship_type`
            added.
        """
        context = super().get_context_data(**kwargs)
        context["person"] = Person.objects.get(id=self.kwargs["person_id"])
        context["relationship_type"] = self.request.GET.get("type", "")
        return context


class AddParentView(CreateView):
    """Form to add a parent relationship for a given person."""

    model = Relationship
    form_class = ParentForm
    template_name = "fh/forms/add_parent.html"

    def get_form_kwargs(self):
        """Pass the related person's ID through to `ParentForm`.

        Returns:
            The form kwargs, with `related_person_id` added.
        """
        kwargs = super().get_form_kwargs()
        kwargs["related_person_id"] = self.kwargs["related_person_id"]
        return kwargs

    def get_initial(self):
        """Pre-fill the related person and relationship type.

        Returns:
            The initial form data, with `related_person` and `type` set.
        """
        initial = super().get_initial()
        initial["related_person"] = self.kwargs["related_person_id"]
        initial["type"] = self.request.GET.get("type", "")
        return initial

    def form_valid(self, form):
        """Set `related_person` from the URL before saving the new relationship.

        Args:
            form: The validated `ParentForm`.

        Returns:
            The redirect response from the parent implementation.
        """
        form.instance.related_person_id = self.kwargs["related_person_id"]
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect back to the related person's detail page after saving.

        Returns:
            The URL of the related person's detail page.
        """
        return reverse_lazy(
            "fh:person_detail", kwargs={"person_id": self.kwargs["related_person_id"]}
        )

    def get_context_data(self, **kwargs):
        """Add the related person and requested relationship type to the context.

        Returns:
            The template context, with `related_person` and
            `relationship_type` added.
        """
        context = super().get_context_data(**kwargs)
        context["related_person"] = Person.objects.get(
            id=self.kwargs["related_person_id"]
        )
        context["relationship_type"] = self.request.GET.get("type", "")
        return context
