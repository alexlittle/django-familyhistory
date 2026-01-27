from django.db import models
from django.utils.translation import gettext_lazy as _

from tinymce.models import HTMLField

from . import Person
from .utils import DATE_MONTH_CHOICES, RELATIONSHIP_CHOICES, format_partial_date


class Relationship(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='relationships_person')
    related_person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='relationships_related_person')
    type = models.CharField(choices=RELATIONSHIP_CHOICES, max_length=100)
    description = HTMLField(blank=True)

    start_year = models.IntegerField(null=True, blank=True)
    start_month = models.IntegerField(null=True, blank=True, choices=DATE_MONTH_CHOICES)
    start_day = models.IntegerField(null=True, blank=True)
    start_date_is_approximate = models.BooleanField(default=False)
    start_date_description = models.CharField(max_length=100, blank=True)

    end_year = models.IntegerField(null=True, blank=True)
    end_month = models.IntegerField(null=True, blank=True, choices=DATE_MONTH_CHOICES)
    end_day = models.IntegerField(null=True, blank=True)
    end_date_is_approximate = models.BooleanField(default=False)
    end_date_description = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Relationship')
        verbose_name_plural = _('Relationships')
        constraints = [
            models.UniqueConstraint(
                fields=['person', 'type', 'related_person'],
                name='unique_relationship',
            )
        ]

    def format_start_date(self):
        return format_partial_date(
            self.start_year, self.start_month, self.start_day, self.start_date_is_approximate
        )

    def format_end_date(self):
        return format_partial_date(
            self.end_year, self.end_month, self.end_day, self.end_date_is_approximate
        )

    def __str__(self):
        return f"{self.person} - {self.related_person}"

