from django import forms

class PersonSearchForm(forms.Form):
    search = forms.CharField(
        label='',
        widget=forms.TextInput(
            attrs={
                'id': 'search',
                'type': 'text',
                'placeholder': 'Search for a name...',
                'class': 'form-control',  # Optional: for styling
            }
        ),
        required=False  # Optional: if you want to allow empty searches
    )