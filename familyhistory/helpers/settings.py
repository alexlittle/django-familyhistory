"""Well-known `SiteSetting` keys the app reads, with typed access and defaults."""

from familyhistory.models import SiteSetting

TREE_START_PERSON_ID_KEY = "tree_start_person_id"
HOMEPAGE_PEOPLE_COUNT_KEY = "homepage_people_count"

DEFAULT_HOMEPAGE_PEOPLE_COUNT = 20


def get_tree_start_person_id():
    """Read the person ID the family tree page should open on by default.

    Returns:
        The configured person ID as an `int`, or `None` if unset.
    """
    value = SiteSetting.get(TREE_START_PERSON_ID_KEY)
    return int(value) if value else None


def get_homepage_people_count():
    """Read the number of people to list per page on the homepage.

    Returns:
        The configured count as an `int`, or `DEFAULT_HOMEPAGE_PEOPLE_COUNT`
        if unset.
    """
    value = SiteSetting.get(HOMEPAGE_PEOPLE_COUNT_KEY)
    return int(value) if value else DEFAULT_HOMEPAGE_PEOPLE_COUNT
