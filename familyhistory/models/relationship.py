"""The `Relationship` model: directed edges between two people."""

from typing import ClassVar

from django.db import models
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField

from . import Person
from .mixins import DateRangeModel
from .utils import RELATIONSHIP_CHOICES, format_partial_date


class Relationship(DateRangeModel):
    """A directed, typed edge between two `Person`s.

    `type` is one of `familyhistory.models.utils.RELATIONSHIP_CHOICES`
    (parent/child or partner types). Family-tree structure is derived
    entirely from these edges - see `familyhistory.helpers.tree` - rather
    than stored as a tree itself.
    """

    person = models.ForeignKey(
        Person, on_delete=models.CASCADE, related_name="relationships_person"
    )
    related_person = models.ForeignKey(
        Person, on_delete=models.CASCADE, related_name="relationships_related_person"
    )
    type = models.CharField(choices=RELATIONSHIP_CHOICES, max_length=100)
    description = HTMLField(blank=True)

    class Meta:
        """Model metadata: display names and the person/type/related_person uniqueness constraint."""

        verbose_name = _("Relationship")
        verbose_name_plural = _("Relationships")
        constraints: ClassVar[list] = [
            models.UniqueConstraint(
                fields=["person", "type", "related_person"],
                name="unique_relationship",
            )
        ]

    def format_date(self):
        """Format the relationship's start/end date range for display.

        Returns:
            `"start - end"` if both are known, just `start` if only the
            start is known, or `"?"` if neither is known.
        """
        start = format_partial_date(
            self.start_day,
            self.start_month,
            self.start_year,
            self.start_date_is_approximate,
        )
        end = format_partial_date(
            self.end_day, self.end_month, self.end_year, self.end_date_is_approximate
        )

        if start and end:
            return start + " - " + end
        elif start:
            return start
        else:
            return _("?")

    def __str__(self):
        return f"{self.person} - {self.related_person}"
