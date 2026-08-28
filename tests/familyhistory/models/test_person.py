"""Tests for the Person model."""

import pytest
from django.db import connection

from familyhistory.models.person import Person, photo_path
from familyhistory.models.relationship import Relationship
from familyhistory.models.treecache import TreeCache
from familyhistory.models.utils import DECEASED, LIVING, UNKNOWN

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_person(**kwargs):
    """Unsaved Person, for testing pure-Python methods without a DB hit."""
    defaults = {"first_name": "Robert", "birth_surname": "Smith"}
    defaults.update(kwargs)
    return Person(**defaults)


def create_person(**kwargs):
    """Persisted Person, for relationship tests."""
    defaults = {"first_name": "Robert", "birth_surname": "Smith"}
    defaults.update(kwargs)
    return Person.objects.create(**defaults)


# ---------------------------------------------------------------------------
# photo_path
# ---------------------------------------------------------------------------


class TestPhotoPath:
    def test_uses_lowercased_birth_surname(self):
        person = make_person(birth_surname="MacDonald")
        assert photo_path(person, "portrait.jpg") == "person/macdonald/portrait.jpg"

    def test_falls_back_when_no_birth_surname(self):
        person = make_person(birth_surname="")
        assert photo_path(person, "portrait.jpg") == (
            "person/unknown_birth_surname/portrait.jpg"
        )


# ---------------------------------------------------------------------------
# death_status
# ---------------------------------------------------------------------------


class TestDeathStatus:
    @pytest.mark.parametrize("field", ["death_year", "death_month", "death_day"])
    def test_any_death_date_part_implies_deceased(self, field):
        person = make_person(**{field: 5})
        assert person.death_status == DECEASED

    def test_death_location_implies_deceased(self):
        person = make_person(death_location="Harrogate")
        assert person.death_status == DECEASED

    def test_flag_used_when_no_death_data(self):
        assert make_person(is_deceased=True).death_status == DECEASED
        assert make_person(is_deceased=False).death_status == LIVING

    def test_unknown_when_nothing_known(self):
        assert make_person().death_status == UNKNOWN
        assert make_person(is_deceased=None).death_status == UNKNOWN

    def test_hard_evidence_beats_contradictory_flag(self):
        """A recorded death date wins over is_deceased=False."""
        person = make_person(death_year=1980, is_deceased=False)
        assert person.death_status == DECEASED


# ---------------------------------------------------------------------------
# Display names
# ---------------------------------------------------------------------------


class TestGetDisplayName:
    def test_first_name_and_birth_surname(self):
        person = make_person(first_name="Robert", birth_surname="Smith")
        assert person.get_display_name() == "Robert Smith"

    def test_includes_middle_name(self):
        person = make_person(middle_name="James")
        assert person.get_display_name() == "Robert James Smith"

    def test_known_as_replaces_first_name(self):
        person = make_person(known_as="Bob", middle_name="James")
        assert person.get_display_name() == "Bob James Smith"

    def test_known_as_equal_to_middle_name_is_not_duplicated(self):
        person = make_person(known_as="James", middle_name="James")
        assert person.get_display_name() == "James Smith"

    def test_known_as_without_middle_name(self):
        person = make_person(known_as="Bob")
        assert person.get_display_name() == "Bob Smith"

    def test_current_surname_preferred_over_birth_surname(self):
        person = make_person(birth_surname="Smith", current_surname="Jones")
        assert person.get_display_name() == "Robert Jones"

    def test_second_surname_appended(self):
        person = make_person(birth_surname="Garcia", second_surname="Lopez")
        assert person.get_display_name() == "Robert Garcia Lopez"

    def test_second_surname_appended_after_current_surname(self):
        person = make_person(
            birth_surname="Garcia", current_surname="Marquez", second_surname="Lopez"
        )
        assert person.get_display_name() == "Robert Marquez Lopez"

    def test_no_surname_leaves_trailing_space(self):
        """Documents current behaviour — see notes, this is arguably a bug."""
        person = make_person(birth_surname="", current_surname="")
        assert person.get_display_name() == "Robert "


class TestGetListDisplayName:
    def test_appends_birth_year(self):
        person = make_person(birth_year=1901)
        assert person.get_list_display_name() == "Robert Smith (b.1901)"

    def test_omits_birth_year_when_absent(self):
        assert make_person().get_list_display_name() == "Robert Smith"

    def test_str_matches_list_display_name(self):
        person = make_person(birth_year=1901)
        assert str(person) == person.get_list_display_name()


class TestGetTreeDisplayName:
    def test_unknown_person(self):
        person = make_person(is_unknown=True, first_name="Robert")
        assert person.get_tree_display_name() == "Unknown"

    def test_ignores_known_as_and_middle_name(self):
        person = make_person(known_as="Bob", middle_name="James")
        assert person.get_tree_display_name() == "Robert Smith"

    def test_includes_second_surname(self):
        person = make_person(birth_surname="Garcia", second_surname="Lopez")
        assert person.get_tree_display_name() == "Robert Garcia Lopez"

    def test_ignores_current_surname(self):
        """Tree nodes show the birth surname, not the married one."""
        person = make_person(birth_surname="Smith", current_surname="Jones")
        assert person.get_tree_display_name() == "Robert Smith"


# ---------------------------------------------------------------------------
# Date formatting
# ---------------------------------------------------------------------------


class TestDateFormatting:
    def test_birth_date_falls_back_to_question_mark(self):
        assert make_person().format_birth_date() == "?"

    def test_death_date_falls_back_to_question_mark(self):
        assert make_person().format_death_date() == "?"

    def test_birth_date_uses_year_when_that_is_all_we_have(self):
        assert make_person(birth_year=1901).format_birth_date() == "1901"

    def test_death_date_uses_year_when_that_is_all_we_have(self):
        assert make_person(death_year=1980).format_death_date() == "1980"


class TestGetBirthDeathDate:
    def test_birth_and_death_years(self):
        person = make_person(birth_year=1901, death_year=1980)
        assert person.get_birth_death_date() == "1901–1980"

    def test_living_person_shows_birth_year_only(self):
        person = make_person(birth_year=1901, is_deceased=False)
        assert person.get_birth_death_date() == "1901"

    def test_deceased_without_death_year_shows_question_mark(self):
        person = make_person(birth_year=1901, is_deceased=True)
        assert person.get_birth_death_date() == "1901–?"

    def test_deceased_by_location_without_death_year(self):
        person = make_person(birth_year=1901, death_location="Harrogate")
        assert person.get_birth_death_date() == "1901–?"

    def test_unknown_status_shows_birth_year_only(self):
        person = make_person(birth_year=1901)
        assert person.get_birth_death_date() == "1901"

    def test_unknown_birth_year(self):
        person = make_person(birth_year=None, death_year=1980)
        assert person.get_birth_death_date() == "?–1980"

    def test_nothing_known_at_all(self):
        assert make_person().get_birth_death_date() == "?"


# ---------------------------------------------------------------------------
# Relationships (DB required)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestGetParents:
    def test_returns_both_parents(self):
        child = create_person(first_name="Child")
        father = create_person(first_name="Father")
        mother = create_person(first_name="Mother")
        Relationship.objects.create(
            person=father, related_person=child, type="is_father_of"
        )
        Relationship.objects.create(
            person=mother, related_person=child, type="is_mother_of"
        )

        assert set(child.get_parents()) == {father, mother}

    def test_empty_when_no_parents(self):
        assert list(create_person().get_parents()) == []

    def test_ignores_non_parent_relationships(self):
        child = create_person(first_name="Child")
        spouse = create_person(first_name="Spouse")
        Relationship.objects.create(
            person=spouse, related_person=child, type="is_married_to"
        )

        assert list(child.get_parents()) == []


@pytest.mark.django_db
class TestGetChildren:
    def test_returns_children(self):
        father = create_person(first_name="Father")
        alice = create_person(first_name="Alice")
        bob = create_person(first_name="Bob")
        Relationship.objects.create(
            person=father, related_person=alice, type="is_father_of"
        )
        Relationship.objects.create(
            person=father, related_person=bob, type="is_father_of"
        )

        assert set(father.get_children()) == {alice, bob}

    def test_as_id_list_returns_strings(self):
        father = create_person()
        child = create_person(first_name="Child")
        Relationship.objects.create(
            person=father, related_person=child, type="is_father_of"
        )

        assert father.get_children(as_id_list=True) == [str(child.id)]

    def test_empty_when_childless(self):
        assert list(create_person().get_children()) == []


@pytest.mark.django_db
class TestGetSiblings:
    def test_returns_siblings_excluding_self(self):
        father = create_person(first_name="Father")
        alice = create_person(first_name="Alice")
        bob = create_person(first_name="Bob")
        for child in (alice, bob):
            Relationship.objects.create(
                person=father, related_person=child, type="is_father_of"
            )

        assert list(alice.get_siblings()) == [bob]

    def test_half_siblings_included(self):
        mother = create_person(first_name="Mother")
        father = create_person(first_name="Father")
        alice = create_person(first_name="Alice")
        half = create_person(first_name="Half")

        Relationship.objects.create(
            person=mother, related_person=alice, type="is_mother_of"
        )
        Relationship.objects.create(
            person=father, related_person=alice, type="is_father_of"
        )
        Relationship.objects.create(
            person=father, related_person=half, type="is_father_of"
        )

        assert list(alice.get_siblings()) == [half]

    def test_full_sibling_not_duplicated(self):
        """Sharing two parents must not yield the sibling twice."""
        mother = create_person(first_name="Mother")
        father = create_person(first_name="Father")
        alice = create_person(first_name="Alice")
        bob = create_person(first_name="Bob")

        for parent, rel_type in ((mother, "is_mother_of"), (father, "is_father_of")):
            for child in (alice, bob):
                Relationship.objects.create(
                    person=parent, related_person=child, type=rel_type
                )

        assert list(alice.get_siblings()) == [bob]

    def test_no_parents_means_no_siblings(self):
        assert list(create_person().get_siblings()) == []

    def test_only_child(self):
        father = create_person(first_name="Father")
        alice = create_person(first_name="Alice")
        Relationship.objects.create(
            person=father, related_person=alice, type="is_father_of"
        )

        assert list(alice.get_siblings()) == []


@pytest.mark.django_db
class TestGetParentId:
    def test_returns_mother_id_by_default(self):
        child = create_person(first_name="Child")
        mother = create_person(first_name="Mother")
        Relationship.objects.create(
            person=mother, related_person=child, type="is_mother_of"
        )

        assert child.get_parent_id() == mother.id

    def test_returns_father_id_when_asked(self):
        child = create_person(first_name="Child")
        father = create_person(first_name="Father")
        Relationship.objects.create(
            person=father, related_person=child, type="is_father_of"
        )

        assert child.get_parent_id(type="is_father_of") == father.id

    def test_returns_none_when_missing(self):
        assert create_person().get_parent_id() is None


@pytest.mark.django_db
class TestGetPartners:
    def test_finds_partner_from_either_side_of_the_relationship(self):
        alice = create_person(first_name="Alice")
        bob = create_person(first_name="Bob")
        Relationship.objects.create(
            person=alice, related_person=bob, type="is_married_to"
        )

        assert [p for p, _ in alice.get_partners()] == [bob]
        assert [p for p, _ in bob.get_partners()] == [alice]

    def test_as_id_list_returns_strings(self):
        alice = create_person(first_name="Alice")
        bob = create_person(first_name="Bob")
        Relationship.objects.create(
            person=alice, related_person=bob, type="is_married_to"
        )

        assert alice.get_partners(as_id_list=True) == [str(bob.id)]

    def test_ignores_parent_relationships(self):
        alice = create_person(first_name="Alice")
        child = create_person(first_name="Child")
        Relationship.objects.create(
            person=alice, related_person=child, type="is_mother_of"
        )

        assert alice.get_partners() == []

    def test_ongoing_relationship_sorts_before_ended_one(self):
        alice = create_person(first_name="Alice")
        ex = create_person(first_name="Ex")
        current = create_person(first_name="Current")

        Relationship.objects.create(
            person=alice,
            related_person=ex,
            type="is_married_to",
            start_year=1990,
            end_year=2000,
        )
        Relationship.objects.create(
            person=alice,
            related_person=current,
            type="in_relationship_with",
            start_year=2005,
            end_year=None,
        )

        assert [p for p, _ in alice.get_partners()] == [current, ex]

    def test_ended_relationships_sorted_most_recent_first(self):
        alice = create_person(first_name="Alice")
        first = create_person(first_name="First")
        second = create_person(first_name="Second")

        Relationship.objects.create(
            person=alice,
            related_person=first,
            type="is_married_to",
            start_year=1980,
            end_year=1990,
        )
        Relationship.objects.create(
            person=alice,
            related_person=second,
            type="is_married_to",
            start_year=1995,
            end_year=2005,
        )

        assert [p for p, _ in alice.get_partners()] == [second, first]


@pytest.mark.django_db
class TestGetTree:
    def test_returns_none_without_cache_entry(self):
        assert create_person().get_tree() is None

    def test_returns_cached_tree(self):
        person = create_person()
        TreeCache.objects.create(person=person, tree={"id": person.id})

        assert person.get_tree() == {"id": person.id}


# ---------------------------------------------------------------------------
# get_surname_counts
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestGetSurnameCounts:
    def test_counts_each_surname_field(self):
        create_person(first_name="A", birth_surname="Smith")
        create_person(first_name="B", birth_surname="Jones", current_surname="Smith")
        create_person(first_name="C", birth_surname="Garcia", second_surname="Lopez")

        assert Person.get_surname_counts() == [
            ("Garcia", 1),
            ("Jones", 1),
            ("Lopez", 1),
            ("Smith", 2),
        ]

    def test_includes_other_surnames(self):
        create_person(birth_surname="Smith", other_surnames=["Smyth", "Smithe"])

        assert Person.get_surname_counts() == [
            ("Smith", 1),
            ("Smithe", 1),
            ("Smyth", 1),
        ]

    def test_person_counted_once_per_surname(self):
        """Same surname in several fields must not inflate the count."""
        create_person(
            birth_surname="Smith", current_surname="Smith", other_surnames=["Smith"]
        )

        assert Person.get_surname_counts() == [("Smith", 1)]

    def test_unknown_people_excluded(self):
        create_person(birth_surname="Smith", is_unknown=True)
        create_person(birth_surname="Jones")

        assert Person.get_surname_counts() == [("Jones", 1)]

    def test_blank_surnames_ignored(self):
        create_person(birth_surname="", current_surname="", second_surname="")

        assert Person.get_surname_counts() == []

    def test_results_sorted_alphabetically(self):
        for surname in ("Zebra", "Apple", "Mango"):
            create_person(birth_surname=surname)

        assert [s for s, _ in Person.get_surname_counts()] == [
            "Apple",
            "Mango",
            "Zebra",
        ]


# ---------------------------------------------------------------------------
# search — MySQL only (uses MATCH ... AGAINST)
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
@pytest.mark.skipif(
    connection.vendor != "mysql",
    reason="Person.search uses MySQL full-text MATCH ... AGAINST",
)
class TestSearch:
    def test_matches_on_surname(self):
        target = create_person(first_name="Robert", birth_surname="Fotheringay")
        create_person(first_name="Alice", birth_surname="Jones")

        assert list(Person.search("Fotheringay")) == [target]

    def test_no_match_returns_empty(self):
        create_person(first_name="Robert", birth_surname="Smith")

        assert list(Person.search("Fotheringay")) == []

    def test_matches_on_partial_word_prefix(self):
        """A live-search box shouldn't need the whole word typed."""
        target = create_person(first_name="Barbara", birth_surname="Smith")
        create_person(first_name="Alice", birth_surname="Jones")

        assert list(Person.search("barb")) == [target]

    def test_matches_multiple_word_prefixes(self):
        target = create_person(first_name="Barbara", birth_surname="Fotheringay")
        create_person(first_name="Barbara", birth_surname="Jones")

        assert list(Person.search("barb foth")) == [target]

    def test_query_with_no_word_characters_returns_empty(self):
        create_person(first_name="Robert", birth_surname="Smith")

        assert list(Person.search("!!!")) == []
