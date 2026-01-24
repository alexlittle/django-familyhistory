from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from familyhistory.models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title',
                    'format_start_date',
                    'format_end_date')

    def format_start_date(self, obj):
        return obj.format_start_date()

    format_start_date.short_description = _('Start Date')

    def format_end_date(self, obj):
        return obj.format_end_date()

    format_end_date.short_description = _('End Date')

    fieldsets = (
        (None, {
            'fields': (
                'title',
                'description',
            ),
        }),
        (_('Start Date'), {
            'fields': (
                ('start_year', 'start_month', 'start_day', 'start_date_is_approximate', 'start_date_description'),
            ),
        }),
        (_('End Date'), {
            'fields': (
                ('end_year', 'end_month', 'end_day', 'end_date_is_approximate', 'end_date_description'),
            ),
        }),
        (_('Involved People'), {
            'fields': ('involved',),
        }),
    )

    # Use filter_horizontal for a user-friendly widget
    filter_horizontal = ('involved',)