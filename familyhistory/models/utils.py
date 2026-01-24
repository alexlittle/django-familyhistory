from django.utils.translation import gettext_lazy as _


DATE_MONTH_CHOICES = [
    (1, _('January')),
    (2, _('February')),
    (3, _('March')),
    (4, _('April')),
    (5, _('May')),
    (6, _('June')),
    (7, _('July')),
    (8, _('August')),
    (9, _('September')),
    (10, _('October')),
    (11, _('November')),
    (12, _('December'))
]

RELATIONSHIP_CHOICES = [
    ('is_father_of', _('is father of')),
    ('is_mother_of', _('is mother of')),
    ('is_married_to', _('is married to')),
    ('in_relationship_with', _('in relationship with')),
]


def format_partial_date(year, month, day, is_approx):
    parts = []
    if year:
        parts.append(str(year))
        if month:
            parts.append(f"-{month:02d}")
            if day:
                parts.append(f"-{day:02d}")
    if is_approx:
        return f"circa {''.join(parts)}" if parts else _("Unknown date")
    return ''.join(parts) if parts else _("-")