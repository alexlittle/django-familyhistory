# familyhistory/templatetags/sanitize.py
"""Template filter for stripping unsafe HTML from rich-text fields before display."""

import nh3
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

ALLOWED_TAGS = {
    "p",
    "br",
    "strong",
    "em",
    "u",
    "s",
    "ol",
    "ul",
    "li",
    "a",
    "h2",
    "h3",
    "h4",
    "blockquote",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
}
ALLOWED_ATTRIBUTES = {"a": {"href", "title"}}


@register.filter(is_safe=True)
def sanitize(value):
    """Strip HTML outside `ALLOWED_TAGS`/`ALLOWED_ATTRIBUTES` from a rich-text value.

    Used to safely render `HTMLField` content (e.g. `Person.biography`)
    that was authored via the TinyMCE editor.

    Args:
        value: The rich-text value to sanitize.

    Returns:
        A `SafeString` with disallowed tags/attributes removed, or `""` if
        `value` is falsy.
    """
    if not value:
        return ""
    return mark_safe(
        nh3.clean(str(value), tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
    )
