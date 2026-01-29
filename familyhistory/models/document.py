import os

from django.db import models
from django.utils.translation import gettext_lazy as _

from tinymce.models import HTMLField

from .utils import DATE_MONTH_CHOICES, DOCUMENT_CHOICES, format_partial_date
from .person import Person
from .event import Event


def doc_file_path(instance, filename):
    return f"document/{instance.document.type}/{filename}"


class Document(models.Model):
    title = models.CharField(max_length=200)
    description = HTMLField(blank=True)
    type = models.CharField(choices=DOCUMENT_CHOICES, max_length=100)
    type_other = models.CharField(max_length=100, blank=True)

    person_involved = models.ManyToManyField(Person, related_name='document_people', blank=True)
    event_involved = models.ManyToManyField(Event, related_name='document_event', blank=True)

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
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')


class DocumentFile(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='document_file')
    file = models.FileField(upload_to=doc_file_path)
    title = models.CharField(max_length=200, blank=True)

    def __str__(self):
        if self.title:
            return f"{self.document.title} {self.title}"
        else:
            return f"{self.document.title}"

    class Meta:
        verbose_name = _('Document File')
        verbose_name_plural = _('Document Files')

    def get_filename(self):
        return os.path.basename(self.file.name)