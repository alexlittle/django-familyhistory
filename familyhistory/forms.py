from typing import ClassVar

from django import forms

from .models import Relationship


class PersonSearchForm(forms.Form):
    search = forms.CharField(
        label="",
        widget=forms.TextInput(
            attrs={
                "id": "search",
                "type": "text",
                "placeholder": "Search for a name...",
                "class": "form-control search-field",
            }
        ),
        required=False,
    )


class RelationshipForm(forms.ModelForm):
    class Meta:
        model = Relationship
        fields: ClassVar[list] = ["type", "related_person"]

    def __init__(self, *args, **kwargs):
        kwargs.pop("person_id", None)
        super().__init__(*args, **kwargs)
        self.fields["related_person"].widget = forms.HiddenInput()


class ParentForm(forms.ModelForm):
    class Meta:
        model = Relationship
        fields: ClassVar[list] = ["type", "person"]

    def __init__(self, *args, **kwargs):
        kwargs.pop("related_person_id", None)
        super().__init__(*args, **kwargs)
        self.fields["person"].widget = forms.HiddenInput()
