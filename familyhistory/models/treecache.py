from django.db import models
from django.utils.translation import gettext_lazy as _

from . import Person


class TreeCache(models.Model):

    person = models.OneToOneField(Person, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tree = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = _('TreeCache')
        verbose_name_plural = _('TreeCaches')

    def __str__(self):
        return str(self.person)
