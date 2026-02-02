from rest_framework import serializers
from familyhistory.models import Person


class PersonSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = Person
        fields = ['id',
                  'display_name',
                  'first_name',
                  'middle_name',
                  'birth_surname',
                  'second_surname',
                  'current_surname',
                  'other_surnames',
                  'known_as',
                  'birth_year',
                  ]

    def get_display_name(self, obj):
        return obj.get_display_name()