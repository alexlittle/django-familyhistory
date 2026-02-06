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


DOCUMENT_CHOICES = [
    ('research', _('Research')),
    ('birth_certificate', _('Birth Certificate')),
    ('marriage_certificate', _('Marriage Certificate')),
    ('death_certificate', _('Death Certificate')),
    ('obituary', _('Obituary')),
    ('identity_doc', _('Passport/ID')),
    ('other', _('Other')),
]

GENDER_CHOICES = [
    ('male', _('male')),
    ('female', _('female')),
    ('other', _('other')),
    ('unknown', _('unknown'))
]

def format_partial_date(year, month, day, is_approx):
    if not year and not month and not day:
        return None

    month_names = [
        "", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]

    parts = []
    if year:
        parts.append(str(year))
    if month:
        parts.insert(0, month_names[month])
    if day:
        parts.insert(0, str(day))

    formatted = " ".join(parts)

    if is_approx:
        return f"c. {formatted}" if formatted else _("Unknown date")
    return formatted if formatted else None
