"""The `Event` model: a life event that one or more people were involved in."""

from django.db import models
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField

from .mixins import DateRangeModel
from .person import Person
from .utils import format_partial_date


class Event(DateRangeModel):
    """A life event (e.g. emigration, military service) linked to one or more people."""

    title = models.CharField(max_length=200)
    description = HTMLField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    involved = models.ManyToManyField(Person, related_name="events_involved")

    def format_start_date(self):
        """Format the event's start date for display.

        Returns:
            The formatted start date, or `None` if nothing is recorded.
        """
        return format_partial_date(
            self.start_day,
            self.start_month,
            self.start_year,
            self.start_date_is_approximate,
        )

    def format_end_date(self):
        """Format the event's end date for display.

        Returns:
            The formatted end date, or `None` if nothing is recorded.
        """
        return format_partial_date(
            self.end_day, self.end_month, self.end_year, self.end_date_is_approximate
        )

    def __str__(self):
        return f"{self.title}"

    class Meta:
        """Model metadata: display names."""

        verbose_name = _("Event")
        verbose_name_plural = _("Events")
