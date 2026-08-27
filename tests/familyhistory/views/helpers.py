"""
Shared helpers for familyhistory view tests.

make_person() is a thin factory - every Person field has a usable default
(blank string or "unknown" gender), so it only needs to override what a
given test actually cares about.

FakeForm is a minimal stand-in for a Django ModelForm. It's used by the
AddRelationshipView / AddParentView logic tests so they can exercise
form_valid() (which sets an id on form.instance and saves it) without
needing to know RelationshipForm/ParentForm's real fields. It deliberately
does NOT validate anything - that's the trade-off for not depending on
forms.py.
"""

from familyhistory.models import Person


def make_person(**overrides):
    defaults = {
        "first_name": "Test",
        "birth_surname": "Person",
        "gender": "unknown",
    }
    defaults.update(overrides)
    return Person.objects.create(**defaults)


class FakeForm:
    """Just enough of a ModelForm's interface for form_valid() to work."""

    def __init__(self, instance):
        self.instance = instance

    def save(self, commit=True):
        if commit:
            self.instance.save()
        return self.instance
