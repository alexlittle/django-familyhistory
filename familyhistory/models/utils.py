from django.utils.dates import MONTHS_3
from django.utils.translation import gettext_lazy as _

RELATIONSHIP_CHOICES = [
    ("is_father_of", _("is father of")),
    ("is_mother_of", _("is mother of")),
    ("is_married_to", _("is married to")),
    ("in_relationship_with", _("in relationship with")),
]


DOCUMENT_CHOICES = [
    ("research", _("Research")),
    ("birth_certificate", _("Birth Certificate")),
    ("marriage_certificate", _("Marriage Certificate")),
    ("death_certificate", _("Death Certificate")),
    ("obituary", _("Obituary")),
    ("identity_doc", _("Passport/ID")),
    ("other", _("Other")),
]

GENDER_CHOICES = [
    ("male", _("male")),
    ("female", _("female")),
    ("other", _("other")),
    ("unknown", _("unknown")),
]


LIVING, DECEASED, UNKNOWN = "living", "deceased", "unknown"


def format_partial_date(day, month, year, approximate=False):
    """Format day/month/year where any part may be missing."""
    if not (day or month or year):
        return None

    parts = []
    if day and month:  # a day without a month is meaningless
        parts.append(str(day))
    if month:
        parts.append(str(MONTHS_3[month].title()))
    if year:
        parts.append(str(year))

    text = " ".join(parts)
    return _("c. %(date)s") % {"date": text} if approximate else text
