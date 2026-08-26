"""Template helpers for rendering paginated result sets."""

from django import template

register = template.Library()


@register.simple_tag
def elided_page_range(page_obj, on_each_side=2, on_ends=1):
    """Return page numbers to display, with ellipsis markers for large gaps.

    Args:
        page_obj: The Page instance currently being rendered.
        on_each_side: Number of pages to show either side of the current page.
        on_ends: Number of pages to show at the start and end of the range.

    Returns:
        An iterator of page numbers interspersed with Paginator.ELLIPSIS.
    """
    return page_obj.paginator.get_elided_page_range(
        page_obj.number, on_each_side=on_each_side, on_ends=on_ends
    )
