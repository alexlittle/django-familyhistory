from django.conf import settings

from django.views.generic import ListView, TemplateView

from .models import Person


class HomeView(ListView):
    template_name = 'fh/home.html'
    paginate_by = 20
    context_object_name = 'people'

    def get_queryset(self):
        return Person.objects.all()

