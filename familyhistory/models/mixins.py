"""Abstract model mixins shared by multiple `familyhistory` models."""

from django.db import models
from django.utils.dates import MONTHS


class DateRangeModel(models.Model):
    """Shared start/end partial-date fields and timestamps."""

    start_year = models.IntegerField(null=True, blank=True)
    start_month = models.IntegerField(null=True, blank=True, choices=MONTHS)
    start_day = models.IntegerField(null=True, blank=True)
    start_date_is_approximate = models.BooleanField(default=False)
    start_date_description = models.CharField(max_length=100, blank=True)

    end_year = models.IntegerField(null=True, blank=True)
    end_month = models.IntegerField(null=True, blank=True, choices=MONTHS)
    end_day = models.IntegerField(null=True, blank=True)
    end_date_is_approximate = models.BooleanField(default=False)
    end_date_description = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Marks this model abstract; not a concrete database table."""

        abstract = True
