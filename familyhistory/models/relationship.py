from typing import ClassVar

from django.db import models
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField

from . import Person
from .mixins import DateRangeModel
from .utils import RELATIONSHIP_CHOICES, format_partial_date


class Relationship(DateRangeModel):
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE, related_name="relationships_person"
    )
    related_person = models.ForeignKey(
        Person, on_delete=models.CASCADE, related_name="relationships_related_person"
    )
    type = models.CharField(choices=RELATIONSHIP_CHOICES, max_length=100)
    description = HTMLField(blank=True)

    class Meta:
        verbose_name = _("Relationship")
        verbose_name_plural = _("Relationships")
        constraints: ClassVar[list] = [
            models.UniqueConstraint(
                fields=["person", "type", "related_person"],
                name="unique_relationship",
            )
        ]

    def format_date(self):

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
