"""DRF serializers exposing `Person` data to the API views."""

from typing import ClassVar

from rest_framework import serializers

from familyhistory.models import Person


class PersonSerializer(serializers.ModelSerializer):
    """Serialize a `Person` for the tree widget and search results."""

    display_name = serializers.SerializerMethodField()
    birth_death_date = serializers.SerializerMethodField()

    class Meta:
        """Model metadata: bound model and exposed fields."""

        model = Person
        fields: ClassVar[list] = [
            "id",
            "display_name",
            "first_name",
            "middle_name",
            "birth_surname",
            "second_surname",
            "current_surname",
            "other_surnames",
            "known_as",
            "birth_year",
            "birth_death_date",
        ]

    def get_display_name(self, obj):
        """Resolve the `display_name` field.

        Args:
            obj: The `Person` being serialized.

        Returns:
            The person's display name.
        """
        return obj.get_display_name()

    def get_birth_death_date(self, obj):
        """Resolve the `birth_death_date` field.

        Args:
            obj: The `Person` being serialized.

        Returns:
            The person's compact birth-death date string.
        """
        return obj.get_birth_death_date()
