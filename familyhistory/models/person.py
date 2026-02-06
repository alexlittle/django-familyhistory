from django.db import models
from django.db.models import F, Func
from collections import Counter
from django.utils.translation import gettext_lazy as _

from tinymce.models import HTMLField

from .utils import DATE_MONTH_CHOICES, format_partial_date, GENDER_CHOICES


def photo_path(instance, filename):
    if instance.birth_surname:
        return f"person/{instance.birth_surname.lower()}/{filename}"
    else:
        return f"person/unknown_birth_surname/{filename}"


class Person(models.Model):
    first_name = models.CharField(max_length=100, blank=True)
    middle_name = models.CharField(max_length=100, blank=True)
    birth_surname = models.CharField(max_length=100, blank=True)
    second_surname = models.CharField(max_length=100, blank=True)
    current_surname = models.CharField(max_length=100, blank=True)
    other_surnames = models.JSONField(default=list, blank=True)
    known_as = models.CharField(max_length=100, blank=True)
    is_unknown = models.BooleanField(default=False)
    gender = models.CharField(choices=GENDER_CHOICES, default="unknown", max_length=20)

    birth_year = models.IntegerField(null=True, blank=True)
    description = HTMLField(blank=True)
    photo = models.ImageField(upload_to=photo_path, blank=True)


    # Birth fields
    birth_year = models.IntegerField(null=True, blank=True)
    birth_month = models.IntegerField(null=True, blank=True, choices=DATE_MONTH_CHOICES)
    birth_day = models.IntegerField(null=True, blank=True)
    birth_is_approximate = models.BooleanField(default=False)
    birth_date_description = models.CharField(max_length=100, blank=True)
    birth_location = models.CharField(max_length=200, blank=True)

    # Death date fields
    death_year = models.IntegerField(null=True, blank=True)
    death_month = models.IntegerField(null=True, blank=True, choices=DATE_MONTH_CHOICES)
    death_day = models.IntegerField(null=True, blank=True)
    death_is_approximate = models.BooleanField(default=False)
    death_date_description = models.CharField(max_length=100, blank=True)
    death_location = models.CharField(max_length=200, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Person')
        verbose_name_plural = _('People')
        ordering = ('birth_year', 'birth_month', 'birth_day')

    def __str__(self):
        return self.get_list_display_name()

    def get_list_display_name(self):
        display_name = self.get_display_name()
        if self.birth_year:
            display_name += f" (b.{self.birth_year})"
        return display_name

    def get_display_name(self):
        if self.known_as:
            if self.known_as != self.middle_name:
                display_name = f"{self.known_as} {self.middle_name}" if self.middle_name else f"{self.known_as}"
            else:
                display_name = f"{self.known_as}"
        else:
            display_name = f"{self.first_name} {self.middle_name}" if self.middle_name else f"{self.first_name}"

        if self.current_surname:
            display_name += f" {self.current_surname}"
        else:
            display_name += f" {self.birth_surname}"

        if self.second_surname:
            display_name += f" {self.second_surname}"

        return display_name

    def get_tree_display_name(self):
        if self.is_unknown:
            return _("Unknown")

        display_name = f"{self.first_name} {self.birth_surname}"
        if self.second_surname:
            display_name += f" {self.second_surname}"
        return display_name

    def format_birth_date(self):
        return format_partial_date(
            self.birth_year, self.birth_month, self.birth_day, self.birth_is_approximate
        )

    def format_death_date(self):
        return format_partial_date(
            self.death_year, self.death_month, self.death_day, self.death_is_approximate
        )

    def get_partners(self, as_id_list=False):
        partner_relationships = []

        # Find relationships where self is the person
        relationships_as_person = self.relationships_person.filter(
            type__in=['is_married_to', 'in_relationship_with']
        )
        for relationship in relationships_as_person:
            partner = relationship.related_person
            partner_relationships.append((partner, relationship))

        relationships_as_related_person = self.relationships_related_person.filter(
            type__in=['is_married_to', 'in_relationship_with']
        )
        for relationship in relationships_as_related_person:
            partner = relationship.person
            partner_relationships.append((partner, relationship))

        partner_relationships.sort(
            key=lambda x: (
                x[1].end_year is None,
                x[1].start_year or 9999,
                x[1].start_month or 12,
                x[1].start_day or 31
            ),
            reverse=True
        )

        if as_id_list:
            # Extract the ID from the partner object and convert to string
            return [str(partner.id) for partner, relationship in partner_relationships]
        return partner_relationships

    def get_parents(self):
        # Get the IDs of all parents
        parent_ids = self.relationships_related_person.filter(
            type__in=['is_father_of', 'is_mother_of']
        ).values_list('person_id', flat=True)

        # Fetch the parent Person objects
        parents = Person.objects.filter(id__in=parent_ids).distinct()
        return parents

    def get_siblings(self):
        from .relationship import Relationship
        # Get the IDs of all parents of the current person
        parent_ids = self.relationships_related_person.filter(
            type__in=['is_father_of', 'is_mother_of']
        ).values_list('person_id', flat=True)

        # If no parents, return an empty queryset
        if not parent_ids:
            return Person.objects.none()

        # Find all children of these parents (siblings)
        sibling_ids = Relationship.objects.filter(
            person_id__in=parent_ids,
            type__in=['is_father_of', 'is_mother_of']
        ).values_list('related_person_id', flat=True)

        # Exclude the current person from the siblings list
        siblings = Person.objects.filter(id__in=sibling_ids).exclude(id=self.id).distinct()

        return siblings

    def get_parent_id(self, type="is_mother_of"):
        from .relationship import Relationship
        try:
            father = Relationship.objects.get(
                related_person=self,
                type=type)
            return father.person.id
        except Relationship.DoesNotExist:
            return None

    def get_children(self, as_id_list=False):
        from .relationship import Relationship

        # Find all relationships where the current person is the parent
        children_relationships = Relationship.objects.filter(
            person=self,
            type__in=['is_father_of', 'is_mother_of']
        )

        # Extract the IDs of the children
        children_ids = children_relationships.values_list('related_person_id', flat=True)

        # Fetch the children Person objects
        children = Person.objects.filter(id__in=children_ids).distinct()
        if as_id_list:
            return [str(c_id) for c_id in children.values_list('id', flat=True)]
        return children

    def get_tree(self):
        from .treecache import TreeCache
        try:
            tree_obj = TreeCache.objects.get(person=self)
            return tree_obj.tree
        except TreeCache.DoesNotExist:
            return None

    @staticmethod
    def get_surname_counts():
        known_people = Person.objects.filter(is_unknown=False)
        # For each person, collect all unique surnames
        person_surnames = []
        for person in known_people:
            surnames = set()
            if person.birth_surname:
                surnames.add(person.birth_surname)
            if person.second_surname:
                surnames.add(person.second_surname)
            if person.current_surname:
                surnames.add(person.current_surname)
            if person.other_surnames:
                surnames.update(person.other_surnames)
            person_surnames.append(surnames)

        # Count how many people have each surname
        surname_counts = Counter()
        for surnames in person_surnames:
            for surname in surnames:
                surname_counts[surname] += 1

        # Sort the surnames alphabetically
        sorted_surname_counts = sorted(surname_counts.items(), key=lambda x: x[0])

        return sorted_surname_counts

    @staticmethod
    def search(query):
        return Person.objects.extra(
            where=[
                "MATCH(first_name, middle_name, birth_surname, second_surname, current_surname, known_as) AGAINST (%s IN NATURAL LANGUAGE MODE)"],
            params=[query]
        )


