"""The `Person` model: the core entity everything else attaches to."""

import re
from collections import Counter

from django.db import models
from django.utils.dates import MONTHS
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField

from .utils import DECEASED, GENDER_CHOICES, LIVING, UNKNOWN, format_partial_date


def photo_path(instance, filename):
    """Build the upload path for a `Person`'s photo, grouped by surname.

    Args:
        instance: The `Person` the photo is being uploaded for.
        filename: Original uploaded filename.

    Returns:
        The relative storage path for the file.
    """
    if instance.birth_surname:
        return f"person/{instance.birth_surname.lower()}/{filename}"
    else:
        return f"person/unknown_birth_surname/{filename}"


class Person(models.Model):
    """A person recorded in the family history, living or deceased.

    Names are split into several optional fields rather than a single
    "full name", because historical records rarely agree on how a
    person's name should be written. Life/death dates are similarly split
    into separate nullable year/month/day fields with an
    `*_is_approximate` flag, since genealogical dates are often partial or
    uncertain - see `familyhistory.models.utils.format_partial_date`.
    """

    first_name = models.CharField(max_length=100, blank=True)
    middle_name = models.CharField(max_length=100, blank=True)
    birth_surname = models.CharField(max_length=100, blank=True)
    second_surname = models.CharField(max_length=100, blank=True)
    current_surname = models.CharField(max_length=100, blank=True)
    other_surnames = models.JSONField(default=list, blank=True)
    known_as = models.CharField(max_length=100, blank=True)
    is_unknown = models.BooleanField(default=False)
    gender = models.CharField(choices=GENDER_CHOICES, default="unknown", max_length=20)

    biography = HTMLField(blank=True)
    photo = models.ImageField(upload_to=photo_path, blank=True)

    # Birth fields
    birth_year = models.IntegerField(null=True, blank=True)
    birth_month = models.IntegerField(null=True, blank=True, choices=MONTHS)
    birth_day = models.IntegerField(null=True, blank=True)
    birth_is_approximate = models.BooleanField(default=False)
    birth_date_description = models.CharField(max_length=100, blank=True)
    birth_location = models.CharField(max_length=200, blank=True)

    # Death date fields
    death_year = models.IntegerField(null=True, blank=True)
    death_month = models.IntegerField(null=True, blank=True, choices=MONTHS)
    death_day = models.IntegerField(null=True, blank=True)
    death_is_approximate = models.BooleanField(default=False)
    death_date_description = models.CharField(max_length=100, blank=True)
    death_location = models.CharField(max_length=200, blank=True)
    is_deceased = models.BooleanField(null=True, blank=True, default=None)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Model metadata: display names and default ordering."""

        verbose_name = _("Person")
        verbose_name_plural = _("People")
        ordering = ("birth_year", "birth_month", "birth_day")

    def __str__(self):
        return self.get_list_display_name()

    @property
    def death_status(self):
        """Whether this person is living, deceased, or unknown.

        Hard evidence (a death date or location) takes priority; failing
        that, falls back to the `is_deceased` flag, and finally to
        `UNKNOWN` if nothing is recorded either way.

        Returns:
            One of `familyhistory.models.utils.LIVING`,
            `familyhistory.models.utils.DECEASED`, or
            `familyhistory.models.utils.UNKNOWN`.
        """
        # Hard evidence first — a date or place of death settles it
        if self.death_year or self.death_month or self.death_day:
            return DECEASED
        if self.death_location:
            return DECEASED

        # No death data — fall back to the flag
        if self.is_deceased is True:
            return DECEASED
        if self.is_deceased is False:
            return LIVING

        return UNKNOWN

    def get_list_display_name(self):
        """Display name for list views, suffixed with the birth year if known.

        Returns:
            The display name, e.g. "Jane Smith (b.1892)".
        """
        display_name = self.get_display_name()
        if self.birth_year:
            display_name += f" (b.{self.birth_year})"
        return display_name

    def get_display_name(self):
        """Build this person's preferred display name.

        Prefers `known_as` over `first_name` for the given name, and
        `current_surname` over `birth_surname` for the family name, with
        `second_surname` appended when set.

        Returns:
            The assembled display name.
        """
        if self.known_as:
            if self.known_as != self.middle_name:
                display_name = (
                    f"{self.known_as} {self.middle_name}"
                    if self.middle_name
                    else f"{self.known_as}"
                )
            else:
                display_name = f"{self.known_as}"
        else:
            display_name = (
                f"{self.first_name} {self.middle_name}"
                if self.middle_name
                else f"{self.first_name}"
            )

        if self.current_surname:
            display_name += f" {self.current_surname}"
        else:
            display_name += f" {self.birth_surname}"

        if self.second_surname:
            display_name += f" {self.second_surname}"

        return display_name

    def get_tree_display_name(self):
        """Display name for tree nodes: birth name only, not `known_as`.

        Returns:
            `"Unknown"` if `is_unknown` is set, otherwise the person's
            first and birth (and, if set, second) surname.
        """
        if self.is_unknown:
            return _("Unknown")

        display_name = f"{self.first_name} {self.birth_surname}"
        if self.second_surname:
            display_name += f" {self.second_surname}"
        return display_name

    def format_birth_date(self):
        """Format the birth date for display.

        Returns:
            The formatted birth date, or `"?"` if nothing is recorded.
        """
        response = format_partial_date(
            self.birth_day, self.birth_month, self.birth_year, self.birth_is_approximate
        )
        return response if response else "?"

    def format_death_date(self):
        """Format the death date for display.

        Returns:
            The formatted death date, or `"?"` if nothing is recorded.
        """
        response = format_partial_date(
            self.death_day, self.death_month, self.death_year, self.death_is_approximate
        )
        return response if response else "?"

    def get_birth_death_date(self):
        """Compact lifespan for tree nodes and list views.

        Returns:
            A `"birth–death"` string (e.g. `"1892–1970"`), using `"?"` for
            an unknown but expected death date, or just the birth portion
            if the person is still living.
        """
        status = self.death_status

        if self.birth_year:
            birth = format_partial_date(
                None, None, self.birth_year, self.birth_is_approximate
            )
        else:
            birth = "?"

        if status == LIVING:
            death = ""
        elif self.death_year:
            death = format_partial_date(
                None, None, self.death_year, self.death_is_approximate
            )
        elif status == DECEASED:
            death = "?"
        else:
            death = ""

        if death:
            return f"{birth}–{death}"
        return birth

    def get_partners(self, as_id_list=False):
        """Find this person's partners, most recent/current relationship first.

        Looks at `Relationship` rows in both directions (this person as
        `person` or as `related_person`) with a partner type.

        Args:
            as_id_list: If `True`, return partner IDs as strings instead of
                `(Person, Relationship)` tuples.

        Returns:
            A list of `(Person, Relationship)` tuples, or a list of partner
            ID strings if `as_id_list` is `True`.
        """
        partner_relationships = []

        # Find relationships where self is the person
        relationships_as_person = self.relationships_person.filter(
            type__in=["is_married_to", "in_relationship_with"]
        )
        for relationship in relationships_as_person:
            partner = relationship.related_person
            partner_relationships.append((partner, relationship))

        relationships_as_related_person = self.relationships_related_person.filter(
            type__in=["is_married_to", "in_relationship_with"]
        )
        for relationship in relationships_as_related_person:
            partner = relationship.person
            partner_relationships.append((partner, relationship))

        partner_relationships.sort(
            key=lambda x: (
                x[1].end_year is None,
                x[1].start_year or 9999,
                x[1].start_month or 12,
                x[1].start_day or 31,
            ),
            reverse=True,
        )

        if as_id_list:
            # Extract the ID from the partner object and convert to string
            return [str(partner.id) for partner, relationship in partner_relationships]
        return partner_relationships

    def get_parents(self):
        """Find this person's parents via `is_father_of`/`is_mother_of` relationships.

        Returns:
            A `Person` queryset of this person's parents.
        """
        # Get the IDs of all parents
        parent_ids = self.relationships_related_person.filter(
            type__in=["is_father_of", "is_mother_of"]
        ).values_list("person_id", flat=True)

        # Fetch the parent Person objects
        parents = Person.objects.filter(id__in=parent_ids).distinct()
        return parents

    def get_siblings(self):
        """Find this person's siblings: other children of the same parents.

        Returns:
            A `Person` queryset of this person's siblings, excluding this
            person, or an empty queryset if no parents are recorded.
        """
        from .relationship import Relationship

        # Get the IDs of all parents of the current person
        parent_ids = self.relationships_related_person.filter(
            type__in=["is_father_of", "is_mother_of"]
        ).values_list("person_id", flat=True)

        # If no parents, return an empty queryset
        if not parent_ids:
            return Person.objects.none()

        # Find all children of these parents (siblings)
        sibling_ids = Relationship.objects.filter(
            person_id__in=parent_ids, type__in=["is_father_of", "is_mother_of"]
        ).values_list("related_person_id", flat=True)

        # Exclude the current person from the siblings list
        siblings = (
            Person.objects.filter(id__in=sibling_ids).exclude(id=self.id).distinct()
        )

        return siblings

    def get_parent_id(self, type="is_mother_of"):
        """Look up a single parent's ID by relationship type.

        Args:
            type: The parent relationship type to look up, either
                `"is_father_of"` or `"is_mother_of"`.

        Returns:
            The parent `Person`'s ID, or `None` if no such relationship
            exists.
        """
        from .relationship import Relationship

        try:
            father = Relationship.objects.get(related_person=self, type=type)
            return father.person.id
        except Relationship.DoesNotExist:
            return None

    def get_children(self, as_id_list=False):
        """Find this person's children via `is_father_of`/`is_mother_of` relationships.

        Args:
            as_id_list: If `True`, return child IDs as strings instead of
                a queryset.

        Returns:
            A `Person` queryset of this person's children, or a list of
            child ID strings if `as_id_list` is `True`.
        """
        from .relationship import Relationship

        # Find all relationships where the current person is the parent
        children_relationships = Relationship.objects.filter(
            person=self, type__in=["is_father_of", "is_mother_of"]
        )

        # Extract the IDs of the children
        children_ids = children_relationships.values_list(
            "related_person_id", flat=True
        )

        # Fetch the children Person objects
        children = Person.objects.filter(id__in=children_ids).distinct()
        if as_id_list:
            return [str(c_id) for c_id in children.values_list("id", flat=True)]
        return children

    def get_tree(self):
        """Look up this person's precomputed tree from `TreeCache`.

        Note this only reads what `manage.py generate_tree` has stored;
        nothing populates `TreeCache` automatically.

        Returns:
            The cached tree JSON, or `None` if no cache entry exists.
        """
        from .treecache import TreeCache

        try:
            tree_obj = TreeCache.objects.get(person=self)
            return tree_obj.tree
        except TreeCache.DoesNotExist:
            return None

    @staticmethod
    def get_surname_counts():
        """Count how many known people share each surname.

        Considers `birth_surname`, `second_surname`, `current_surname`,
        and `other_surnames` (each person is counted at most once per
        surname), and excludes people flagged `is_unknown`.

        Returns:
            A list of `(surname, count)` tuples, sorted alphabetically by
            surname.
        """
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
        """Full-text prefix search people by name fields.

        Each word in `query` is matched as a required prefix (boolean mode's
        `word*`) rather than a whole word, so a live-search box gets results
        as soon as a few characters are typed (e.g. "barb" matches
        "Barbara") instead of only once the full word is entered, which is
        all natural language mode allows.

        Args:
            query: The raw search text. Non-word characters are stripped
                out before building the `MATCH ... AGAINST` boolean query,
                so user input can't inject boolean-mode operators.

        Returns:
            A `Person` queryset matching the query, or an empty queryset if
            it contained no searchable words.
        """
        words = re.findall(r"\w+", query)
        if not words:
            return Person.objects.none()

        boolean_query = " ".join(f"+{word}*" for word in words)

        return Person.objects.extra(
            where=[
                "MATCH(first_name, middle_name, birth_surname, second_surname, current_surname, known_as) AGAINST (%s IN BOOLEAN MODE)"
            ],
            params=[boolean_query],
        )
