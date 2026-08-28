"""Forms for the live person-search box and add-relationship/add-parent pages."""

from typing import ClassVar

from django import forms

from .models import Relationship


class PersonSearchForm(forms.Form):
    """Single search-box form used by the home, search, and surname pages."""

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
    """Add a partner or child `Relationship` from a given source person.

    `related_person` is set via the view (hidden in the rendered form)
    rather than chosen by the user, so it's hidden here and the extra
    `person_id` kwarg the view passes is discarded before the standard
    `ModelForm` init runs.
    """

    class Meta:
        """Model metadata: bound model and editable fields."""

        model = Relationship
        fields: ClassVar[list] = ["type", "related_person"]

    def __init__(self, *args, **kwargs):
        kwargs.pop("person_id", None)
        super().__init__(*args, **kwargs)
        self.fields["related_person"].widget = forms.HiddenInput()


class ParentForm(forms.ModelForm):
    """Add a parent `Relationship` for a given related person.

    `person` (the parent) is set via the view rather than chosen by the
    user, so it's hidden here and the extra `related_person_id` kwarg the
    view passes is discarded before the standard `ModelForm` init runs.
    """

    class Meta:
        """Model metadata: bound model and editable fields."""

        model = Relationship
        fields: ClassVar[list] = ["type", "person"]

    def __init__(self, *args, **kwargs):
        kwargs.pop("related_person_id", None)
        super().__init__(*args, **kwargs)
        self.fields["person"].widget = forms.HiddenInput()
