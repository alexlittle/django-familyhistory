from django.db import models
from django.utils.translation import gettext_lazy as _

from tinymce.models import HTMLField

from .utils import DATE_MONTH_CHOICES, format_partial_date
from .person import Person


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = HTMLField(blank=True)
    involved = models.ManyToManyField(Person, related_name='events_involved')

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

    def format_start_date(self):
        return format_partial_date(
            self.start_year, self.start_month, self.start_day, self.start_date_is_approximate
        )

    def format_end_date(self):
        return format_partial_date(
            self.end_year, self.end_month, self.end_day, self.end_date_is_approximate
        )

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = _('Event')
        verbose_name_plural = _('Events')