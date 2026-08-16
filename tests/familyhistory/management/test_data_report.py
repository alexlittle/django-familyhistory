"""Tests for the "missing data" report management command.

Adjust COMMAND_NAME and the Command import below to match your actual
module name under familyhistory/management/commands/.

These tests require:
  - django.contrib.sites in INSTALLED_APPS with SITE_ID set
  - the admin URLs routed, since person_link() reverses
    admin:familyhistory_person_change
"""

from io import StringIO

import pytest
from django.contrib.sites.models import Site
from django.core.management import call_command
from django.urls import reverse
from django.utils import translation

from familyhistory.models import Person
from familyhistory.models.utils import DECEASED
from familyhistory.management.commands.data_report import Command, hyperlink

COMMAND_NAME = "data_report"


# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------

class TtyStringIO(StringIO):
    """A StringIO that claims to be a terminal, to exercise the OSC 8 branch."""

    def isatty(self):
        return True


@pytest.fixture(autouse=True)
def english():
    """Pin the language so assertions on translated strings are stable."""
    with translation.override("en"):
        yield


@pytest.fixture
def site(db):
    Site.objects.clear_cache()
    current = Site.objects.get_current()
    current.domain = "family.example.com"
    current.save()
    Site.objects.clear_cache()
    yield current
    Site.objects.clear_cache()


def run(method_name, tty=False):
    """Run a single command method and return what it wrote to stdout."""
    out = TtyStringIO() if tty else StringIO()
    command = Command(stdout=out, no_color=True)
    getattr(command, method_name)()
    return out.getvalue()


def create_person(**kwargs):
    defaults = {"first_name": "Robert", "birth_surname": "Smith", "birth_year": 1901}
    defaults.update(kwargs)
    return Person.objects.create(**defaults)


def assert_reported(output, person, message):
    """Assert the report names `person` alongside `message` on one line."""
    lines = [line for line in output.splitlines() if message in line]
    assert lines, f"no line containing {message!r} in:\n{output}"
    assert any(
        person.get_display_name() in line and f"/{person.pk}/" in line
        for line in lines
    ), f"{person} not reported for {message!r}:\n{output}"

# ---------------------------------------------------------------------------
# hyperlink
# ---------------------------------------------------------------------------

class TestHyperlink:
    def test_wraps_text_in_osc8_sequence(self):
        assert hyperlink("Robert Smith", "https://example.com/x") == (
            "\033]8;;https://example.com/x\033\\Robert Smith\033]8;;\033\\"
        )

    def test_text_is_visible_between_the_escapes(self):
        result = hyperlink("Robert Smith", "https://example.com/x")
        assert "Robert Smith" in result
        assert result.startswith("\033]8;;")
        assert result.endswith("\033]8;;\033\\")


# ---------------------------------------------------------------------------
# person_link
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestPersonLink:
    def test_non_tty_output_shows_bare_url(self, site):
        person = create_person()
        command = Command(stdout=StringIO(), no_color=True)

        path = reverse("admin:familyhistory_person_change", args=[person.pk])
        expected = f"Robert Smith <https://family.example.com{path}>"

        assert command.person_link(person) == expected

    def test_tty_output_uses_osc8_hyperlink(self, site):
        person = create_person()
        command = Command(stdout=TtyStringIO(), no_color=True)

        result = command.person_link(person)

        assert result.startswith("\033]8;;https://family.example.com/")
        assert "Robert Smith" in result
        assert "<https://" not in result

    def test_uses_display_name_not_list_display_name(self, site):
        """No "(b.1901)" suffix — person_link calls get_display_name()."""
        person = create_person(birth_year=1901)
        command = Command(stdout=StringIO(), no_color=True)

        assert "(b.1901)" not in command.person_link(person)

    def test_url_points_at_the_right_person(self, site):
        create_person(first_name="Alice")
        target = create_person(first_name="Bob")
        command = Command(stdout=StringIO(), no_color=True)

        assert f"/{target.pk}/" in command.person_link(target)


# ---------------------------------------------------------------------------
# missing_birth_dates
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestMissingBirthDates:
    def test_reports_person_with_no_birth_year(self, site):
        person = create_person(birth_year=None)
        output = run("missing_birth_dates")
        assert_reported(output, person, "missing birth year")
        assert "1 person with no birth year" in output

    def test_reports_approximate_birth_year(self, site):
        person = create_person(birth_year=1901, birth_is_approximate=True)
        output = run("missing_birth_dates")
        assert_reported(output, person, "birth year is approximate only")
        assert "1 person with approximate birth year" in output

    def test_exact_birth_year_is_not_reported(self, site):
        create_person(birth_year=1901, birth_is_approximate=False)

        output = run("missing_birth_dates")

        assert "Robert Smith" not in output
        assert "0 people with no birth year" in output
        assert "0 people with approximate birth year" in output

    def test_missing_takes_precedence_over_approximate(self, site):
        """The elif means a missing year is never also counted as approximate."""
        create_person(birth_year=None, birth_is_approximate=True)

        output = run("missing_birth_dates")

        assert "1 person with no birth year" in output
        assert "0 people with approximate birth year" in output

    def test_pluralisation(self, site):
        create_person(first_name="Alice", birth_year=None)
        create_person(first_name="Bob", birth_year=None)

        output = run("missing_birth_dates")

        assert "2 people with no birth year" in output

    def test_empty_database(self, site):
        output = run("missing_birth_dates")

        assert "0 people with no birth year" in output
        assert "0 people with approximate birth year" in output

    def test_heading_always_written(self, site):
        assert "Checking missing birth dates" in run("missing_birth_dates")


# ---------------------------------------------------------------------------
# is_deceased_not_set
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestIsDeceasedNotSet:
    def test_reports_unset_flag(self, site):
        person = create_person(is_deceased=None)
        output = run("is_deceased_not_set")
        assert_reported(output, person, "is_deceased flag not set for")
        assert "1 person with is_deceased flag not set" in output

    @pytest.mark.parametrize("flag", [True, False])
    def test_set_flag_is_not_reported(self, site, flag):
        create_person(is_deceased=flag)

        output = run("is_deceased_not_set")

        assert "Robert Smith" not in output
        assert "0 people with is_deceased flag not set" in output

    def test_pluralisation(self, site):
        create_person(first_name="Alice", is_deceased=None)
        create_person(first_name="Bob", is_deceased=None)

        assert "2 people with is_deceased flag not set" in run("is_deceased_not_set")

    def test_heading_always_written(self, site):
        assert "Checking is_deceased for all persons" in run("is_deceased_not_set")


# ---------------------------------------------------------------------------
# missing_date_of_death
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestMissingDateOfDeath:
    def test_reports_deceased_person_with_no_death_year(self, site):
        person = create_person(is_deceased=True, death_year=None)
        output = run("missing_date_of_death")
        assert_reported(output, person, "missing year of death")
        assert "1 person with no year of death" in output

    def test_deceased_with_death_year_is_not_reported(self, site):
        """Guards against dropping the `death_year is None` conjunct."""
        create_person(is_deceased=True, death_year=1980)

        output = run("missing_date_of_death")

        assert "missing year of death" not in output
        assert "0 people with no year of death" in output

    def test_living_person_is_not_reported_as_missing(self, site):
        create_person(is_deceased=False, death_year=None)

        output = run("missing_date_of_death")

        assert "0 people with no year of death" in output

    def test_unknown_status_is_not_reported_as_missing(self, site):
        """No dates, no location, no flag — nothing to report."""
        person = create_person(is_deceased=None, death_year=None)
        assert person.death_status != DECEASED

        output = run("missing_date_of_death")

        assert "0 people with no year of death" in output

    # --- newly covered by the death_status change -------------------------

    def test_death_location_alone_is_reported(self, site):
        """Known place of death, no year, no flag — now caught."""
        person = create_person(is_deceased=None, death_location="Harrogate")
        assert person.death_status == DECEASED
        output = run("missing_date_of_death")
        assert_reported(output, person, "missing year of death")
        assert "1 person with no year of death" in output

    def test_partial_death_date_without_year_is_reported(self, site):
        """A month but no year still means the year is missing."""
        person = create_person(is_deceased=None, death_year=None, death_month=3)
        assert person.death_status == DECEASED
        output = run("missing_date_of_death")
        assert_reported(output, person, "missing year of death")

    def test_death_location_with_year_is_not_reported(self, site):
        create_person(is_deceased=None, death_location="Harrogate",
                      death_year=1980)

        output = run("missing_date_of_death")

        assert "0 people with no year of death" in output

    def test_contradictory_flag_does_not_suppress_the_report(self, site):
        """death_status treats a recorded death date as settling the matter."""
        person = create_person(
            is_deceased=False, death_year=None, death_location="Harrogate"
        )
        assert person.death_status == DECEASED

        output = run("missing_date_of_death")

        assert "1 person with no year of death" in output

    # --- approximate branch -----------------------------------------------

    def test_approximate_death_year_is_reported(self, site):
        person = create_person(is_deceased=True, death_year=1980,
                               death_is_approximate=True)
        output = run("missing_date_of_death")
        assert_reported(output, person, "year of death is approximate only")
        assert "1 person with approximate year of death" in output

    def test_living_person_flagged_approximate(self, site):
        """Still odd: the elif does not check death_status."""
        create_person(is_deceased=False, death_is_approximate=True)

        output = run("missing_date_of_death")

        assert "year of death is approximate only" in output

    # --- counting ----------------------------------------------------------

    def test_pluralisation(self, site):
        create_person(first_name="Alice", is_deceased=True, death_year=None)
        create_person(first_name="Bob", is_deceased=True, death_year=None)

        assert "2 people with no year of death" in run("missing_date_of_death")

    def test_missing_takes_precedence_over_approximate(self, site):
        create_person(is_deceased=True, death_year=None,
                      death_is_approximate=True)

        output = run("missing_date_of_death")

        assert "1 person with no year of death" in output
        assert "0 people with approximate year of death" in output

    def test_heading_always_written(self, site):
        assert "Checking missing date of death" in run("missing_date_of_death")

# ---------------------------------------------------------------------------
# handle — integration through call_command
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestHandle:
    def test_runs_all_three_checks(self, site):
        out = StringIO()
        call_command(COMMAND_NAME, stdout=out, no_color=True)
        output = out.getvalue()

        assert "Checking missing birth dates" in output
        assert "Checking is_deceased for all persons" in output
        assert "Checking missing date of death" in output

    def test_reports_a_person_across_several_sections(self, site):
        create_person(birth_year=None, is_deceased=None)
        out = StringIO()

        call_command(COMMAND_NAME, stdout=out, no_color=True)
        output = out.getvalue()

        assert "1 person with no birth year" in output
        assert "1 person with is_deceased flag not set" in output

    def test_succeeds_on_empty_database(self, site):
        out = StringIO()
        call_command(COMMAND_NAME, stdout=out, no_color=True)

        assert "0 people with no birth year" in out.getvalue()

    def test_writes_nothing_to_stderr(self, site):
        create_person(birth_year=None)
        out, err = StringIO(), StringIO()

        call_command(COMMAND_NAME, stdout=out, stderr=err, no_color=True)

        assert err.getvalue() == ""
