from rest_framework import serializers
from familyhistory.models import Person

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['id', 'first_name', 'middle_name', 'birth_surname', 'second_surname', 'current_surname', 'other_surnames', 'known_as']