"""Shared choice lists and formatting helpers used across the models package."""

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


# Images, PDFs, and common text/office document formats - the kinds of
# files people actually attach as historical documents/certificates.
ALLOWED_DOCUMENT_FILE_EXTENSIONS = [
    # images
    "jpg",
    "jpeg",
    "png",
    "gif",
    "bmp",
    "tif",
    "tiff",
    "webp",
    # documents
    "pdf",
    "doc",
    "docx",
    "odt",
    "rtf",
    "txt",
    "csv",
]


def format_partial_date(day, month, year, approximate=False):
    """Format day/month/year where any part may be missing.

    Genealogical dates are often only known to the year, or the month and
    year, so this renders whatever combination is available (e.g. "Mar
    1892", "1892") rather than requiring a complete date.

    Args:
        day: Day of month, or `None` if unknown. Ignored unless `month` is
            also given, since a day without a month is meaningless.
        month: Month number (1-12), or `None` if unknown.
        year: Year, or `None` if unknown.
        approximate: Whether the date is approximate, in which case the
            result is prefixed with "c." (circa).

    Returns:
        The formatted date string, or `None` if day, month, and year are
        all missing.
    """
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
