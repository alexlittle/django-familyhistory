from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from tinymce.models import HTMLField

from .utils import DATE_MONTH_CHOICES, format_partial_date


def photo_path(instance, filename):
    if instance.birth_surname:
        return f"person/{instance.birth_surname.lower()}/{filename}"
    else:
        return f"person/unknown_birth_surname/{filename}"

class Person(models.Model):
    first_name = models.CharField(max_length=100, blank=True)
    middle_name = models.CharField(max_length=100, blank=True)
    birth_surname = models.CharField(max_length=100, blank=True)
    current_surname = models.CharField(max_length=100, blank=True)
    other_surnames = models.JSONField(default=list, blank=True)
    known_as = models.CharField(max_length=100, blank=True)
    description = HTMLField(blank=True)
    photo = models.ImageField(upload_to=photo_path, blank=True)

    # Birth date fields
    birth_year = models.IntegerField(null=True, blank=True)
    birth_month = models.IntegerField(null=True, blank=True, choices=DATE_MONTH_CHOICES)
    birth_day = models.IntegerField(null=True, blank=True)
    birth_is_approximate = models.BooleanField(default=False)
    birth_date_description = models.CharField(max_length=100, blank=True)

    # Death date fields
    death_year = models.IntegerField(null=True, blank=True)
    death_month = models.IntegerField(null=True, blank=True, choices=DATE_MONTH_CHOICES)
    death_day = models.IntegerField(null=True, blank=True)
    death_is_approximate = models.BooleanField(default=False)
    death_date_description = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = _('Person')
        verbose_name_plural = _('People')
        ordering = ('birth_year', 'birth_month', 'birth_day')

    def format_birth_date(self):
        return format_partial_date(
            self.birth_year, self.birth_month, self.birth_day, self.birth_is_approximate
        )

    def format_death_date(self):
        return format_partial_date(
            self.death_year, self.death_month, self.death_day, self.death_is_approximate
        )

    def __str__(self):
        return f"{self.first_name} {self.current_surname}"

    def get_partners(self):
        # Get the IDs of all partners
        partner_ids = []
        # Find relationships where self is the person
        relationships_as_person = self.relationships_person.filter(
            type__in=['is_married_to', 'in_relationship_with']
        )
        for relationship in relationships_as_person:
            partner_ids.append(relationship.related_person.id)

        # Find relationships where self is the related_person
        relationships_as_related_person = self.relationships_related_person.filter(
            type__in=['is_married_to', 'in_relationship_with']
        )
        for relationship in relationships_as_related_person:
            partner_ids.append(relationship.person.id)

        # Fetch the partner Person objects
        partners = Person.objects.filter(id__in=partner_ids).distinct()
        return partners

    def get_parents(self):
        # Get the IDs of all parents
        parent_ids = self.relationships_related_person.filter(
            type__in=['is_father_of', 'is_mother_of']
        ).values_list('person_id', flat=True)

        # Fetch the parent Person objects
        parents = Person.objects.filter(id__in=parent_ids).distinct()
        return parents
