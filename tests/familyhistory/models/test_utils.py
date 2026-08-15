"""Tests for familyhistory.models.utils.

No database access is required, so SimpleTestCase is used throughout.
"""

import re

from django.test import SimpleTestCase
from django.utils import translation
from django.utils.dates import MONTHS_3
from django.utils.functional import Promise

from familyhistory.models.utils import (
    DECEASED,
    DOCUMENT_CHOICES,
    GENDER_CHOICES,
    LIVING,
    RELATIONSHIP_CHOICES,
    UNKNOWN,
    format_partial_date,
)


class FormatPartialDateTests(SimpleTestCase):
    """Covers every combination of present/missing date parts."""

    def test_all_parts_present(self):
        self.assertEqual(format_partial_date(15, 3, 1990), "15 Mar 1990")

    def test_combinations(self):
        cases = [
            # (day, month, year, expected)
            (15, 3, 1990, "15 Mar 1990"),
            (None, 3, 1990, "Mar 1990"),
            (None, None, 1990, "1990"),
            (None, 3, None, "Mar"),
            (15, 3, None, "15 Mar"),
            (15, None, 1990, "1990"),   # day dropped: meaningless without a month
        ]
        for day, month, year, expected in cases:
            with self.subTest(day=day, month=month, year=year):
                self.assertEqual(format_partial_date(day, month, year), expected)

    def test_no_parts_returns_none(self):
        self.assertIsNone(format_partial_date(None, None, None))

    def test_falsy_values_treated_as_missing(self):
        """Zeros and empty strings should behave like None."""
        for day, month, year in [(0, 0, 0), ("", "", "")]:
            with self.subTest(day=day, month=month, year=year):
                self.assertIsNone(format_partial_date(day, month, year))

    def test_day_only_returns_empty_string(self):
        """Documents current behaviour: a lone day yields "" rather than None.

        The `not (day or month or year)` guard passes because `day` is truthy,
        but nothing is appended, so `" ".join([])` gives "". If None is the
        intended answer, change the guard to `if not (month or year)`.
        """
        self.assertEqual(format_partial_date(15, None, None), "")

    def test_day_only_approximate_returns_bare_prefix(self):
        """Same edge case, made more visible by the approximate prefix."""
        self.assertEqual(str(format_partial_date(15, None, None, approximate=True)),
                         "c. ")

    def test_returns_plain_string(self):
        self.assertIsInstance(format_partial_date(15, 3, 1990), str)

    def test_month_is_abbreviated_and_title_cased(self):
        for month, expected in [(1, "Jan"), (6, "Jun"), (12, "Dec")]:
            with self.subTest(month=month):
                self.assertEqual(format_partial_date(None, month, None), expected)

    def test_invalid_month_raises_key_error(self):
        """MONTHS_3 only has keys 1-12; anything else blows up loudly."""
        for month in (13, 99, -1):
            with self.subTest(month=month):
                with self.assertRaises(KeyError):
                    format_partial_date(None, month, 1990)

    def test_string_inputs_are_coerced(self):
        """Callers passing strings (e.g. straight from a form) still work."""
        self.assertEqual(format_partial_date("15", 3, "1990"), "15 Mar 1990")


class FormatPartialDateApproximateTests(SimpleTestCase):

    def test_approximate_prefixes_full_date(self):
        self.assertEqual(str(format_partial_date(15, 3, 1990, approximate=True)),
                         "c. 15 Mar 1990")

    def test_approximate_prefixes_year_only(self):
        self.assertEqual(str(format_partial_date(None, None, 1990, approximate=True)),
                         "c. 1990")

    def test_approximate_ignored_when_no_date(self):
        self.assertIsNone(format_partial_date(None, None, None, approximate=True))

    def test_approximate_false_matches_default(self):
        self.assertEqual(format_partial_date(15, 3, 1990, approximate=False),
                         format_partial_date(15, 3, 1990))


class FormatPartialDateTranslationTests(SimpleTestCase):
    """The month name must come from the active language's catalogue."""

    def test_month_follows_active_language(self):
        for code in ("en", "fr", "de", "es"):
            with self.subTest(language=code):
                with translation.override(code):
                    expected = f"1 {MONTHS_3[3].title()} 1990"
                    self.assertEqual(format_partial_date(1, 3, 1990), expected)

    def test_french_month_differs_from_english(self):
        """Guards against MONTHS_3 being replaced by a hard-coded list."""
        with translation.override("en"):
            english = format_partial_date(None, 5, None)
        with translation.override("fr"):
            french = format_partial_date(None, 5, None)
        self.assertNotEqual(english, french)

    def test_approximate_prefix_is_translatable(self):
        """The 'c. ' prefix is wrapped in gettext, so it can be overridden."""
        with translation.override("en"):
            self.assertEqual(str(format_partial_date(None, None, 1990,
                                                     approximate=True)),
                             "c. 1990")


CHOICE_LISTS = {
    "RELATIONSHIP_CHOICES": RELATIONSHIP_CHOICES,
    "DOCUMENT_CHOICES": DOCUMENT_CHOICES,
    "GENDER_CHOICES": GENDER_CHOICES,
}

KEY_RE = re.compile(r"^[a-z][a-z0-9_]*$")


class ChoiceListTests(SimpleTestCase):
    """Structural guarantees that keep migrations and stored data safe."""

    def test_keys_are_unique(self):
        for name, choices in CHOICE_LISTS.items():
            with self.subTest(choices=name):
                keys = [key for key, _label in choices]
                self.assertEqual(len(keys), len(set(keys)))

    def test_keys_are_valid_identifiers(self):
        for name, choices in CHOICE_LISTS.items():
            for key, _label in choices:
                with self.subTest(choices=name, key=key):
                    self.assertRegex(key, KEY_RE)

    def test_keys_fit_in_a_reasonable_max_length(self):
        """Catches a new key that would be silently truncated by the column."""
        for name, choices in CHOICE_LISTS.items():
            for key, _label in choices:
                with self.subTest(choices=name, key=key):
                    self.assertLessEqual(len(key), 30)

    def test_labels_are_lazy(self):
        """Labels must stay lazy so language is resolved at render time,
        not at import time (and so makemigrations output stays stable)."""
        for name, choices in CHOICE_LISTS.items():
            for key, label in choices:
                with self.subTest(choices=name, key=key):
                    self.assertIsInstance(label, Promise)

    def test_labels_are_non_empty(self):
        for name, choices in CHOICE_LISTS.items():
            for key, label in choices:
                with self.subTest(choices=name, key=key):
                    self.assertTrue(str(label).strip())


class ChoiceContentTests(SimpleTestCase):
    """Pin down the keys themselves: changing one is a data migration."""

    def test_relationship_keys(self):
        self.assertEqual(
            [key for key, _label in RELATIONSHIP_CHOICES],
            ["is_father_of", "is_mother_of", "is_married_to",
             "in_relationship_with"],
        )

    def test_document_keys(self):
        self.assertEqual(
            [key for key, _label in DOCUMENT_CHOICES],
            ["research", "birth_certificate", "marriage_certificate",
             "death_certificate", "obituary", "identity_doc", "other"],
        )

    def test_gender_keys(self):
        self.assertEqual(
            [key for key, _label in GENDER_CHOICES],
            ["male", "female", "other", "unknown"],
        )

    def test_english_labels(self):
        with translation.override("en"):
            self.assertEqual(str(dict(RELATIONSHIP_CHOICES)["is_father_of"]),
                             "is father of")
            self.assertEqual(str(dict(DOCUMENT_CHOICES)["identity_doc"]),
                             "Passport/ID")
            self.assertEqual(str(dict(GENDER_CHOICES)["female"]), "female")


class LifeStatusConstantTests(SimpleTestCase):

    def test_values(self):
        self.assertEqual((LIVING, DECEASED, UNKNOWN),
                         ("living", "deceased", "unknown"))

    def test_are_distinct(self):
        self.assertEqual(len({LIVING, DECEASED, UNKNOWN}), 3)

    def test_unknown_matches_gender_unknown_key(self):
        """Both use the literal "unknown"; this catches a drift in one of them."""
        self.assertIn(UNKNOWN, [key for key, _label in GENDER_CHOICES])