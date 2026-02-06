from django import forms
from .models import Person, Relationship

class PersonSearchForm(forms.Form):
    search = forms.CharField(
        label='',
        widget=forms.TextInput(
            attrs={
                'id': 'search',
                'type': 'text',
                'placeholder': 'Search for a name...',
                'class': 'form-control search-field',
            }
        ),
        required=False
    )

class RelationshipForm(forms.ModelForm):
    class Meta:
        model = Relationship
        fields = ['type', 'related_person']

    def __init__(self, *args, **kwargs):
        kwargs.pop('person_id', None)
        super(RelationshipForm, self).__init__(*args, **kwargs)
        self.fields['related_person'].widget = forms.HiddenInput()


class ParentForm(forms.ModelForm):
    class Meta:
        model = Relationship
        fields = ['type', 'person']

    def __init__(self, *args, **kwargs):
        kwargs.pop('related_person_id', None)
        super(ParentForm, self).__init__(*args, **kwargs)
        self.fields['person'].widget = forms.HiddenInput()