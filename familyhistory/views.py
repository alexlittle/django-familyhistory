from django.conf import settings

from django.views.generic import TemplateView



class HomeView(TemplateView):

    template_name = 'fh/home.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        return data