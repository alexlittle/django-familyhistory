from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from familyhistory.models import TreeCache

@admin.register(TreeCache)
class TreeCacheAdmin(admin.ModelAdmin):
    ist_display = ('person_str', 'created_at', 'updated_at')

    def person_str(self, obj):
        return str(obj.person.get_display_name())

    person_str.short_description = _('Person')