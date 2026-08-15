# familyhistory/templatetags/sanitize.py
import nh3
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

ALLOWED_TAGS = {
    "p", "br", "strong", "em", "u", "s", "ol", "ul", "li",
    "a", "h2", "h3", "h4", "blockquote", "table", "thead",
    "tbody", "tr", "th", "td",
}
ALLOWED_ATTRIBUTES = {"a": {"href", "title"}}


@register.filter(is_safe=True)
def sanitize(value):
    if not value:
        return ""
    return mark_safe(
        nh3.clean(str(value), tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
    )