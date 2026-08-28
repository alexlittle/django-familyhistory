"""The `TreeCache` model: a per-person precomputed tree JSON cache."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from . import Person


class TreeCache(models.Model):
    """A cached, precomputed family tree for a single `Person`.

    Populated by `manage.py generate_tree` for cases where recomputing
    the tree live via `familyhistory.helpers.tree.create_tree` is too
    slow. Nothing currently reads from this automatically - check whether
    a view/consumer has been wired up before assuming the cache is live.
    """

    person = models.OneToOneField(Person, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tree = models.JSONField(default=dict, blank=True)

    class Meta:
        """Model metadata: display names."""

        verbose_name = _("TreeCache")
        verbose_name_plural = _("TreeCaches")

    def __str__(self):
        return str(self.person)
