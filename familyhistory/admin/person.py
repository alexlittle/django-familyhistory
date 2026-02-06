from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from familyhistory.models import Person


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('get_display_name',
                    'gender',
                    'is_unknown',
                    'format_birth_date',
                    'format_death_date')
    search_fields = ['first_name',
                    'middle_name',
                    'birth_surname',
                    'second_surname',
                    'current_surname',
                    'known_as']

    def format_birth_date(self, obj):
        return obj.format_birth_date()

    format_birth_date.short_description = _('Birth Date')

    def format_death_date(self, obj):
        return obj.format_death_date()

    format_death_date.short_description = _('Death Date')

    fieldsets = (
        (None, {
            'fields': (
                'first_name',
                'middle_name',
                'birth_surname',
                'second_surname',
                'current_surname',
                'known_as',
                'is_unknown',
                'gender',
                'photo'
            ),
        }),
        (_('Birth Date'), {
            'fields': (
                ('birth_year', 'birth_month', 'birth_day', 'birth_is_approximate', 'birth_date_description'),
                'birth_location',
            ),
        }),
        (_('Death Date'), {
            'fields': (
                ('death_year', 'death_month', 'death_day', 'death_is_approximate', 'death_date_description'),
                'death_location',
            ),
        }),
    )