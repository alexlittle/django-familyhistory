"""
Tests for familyhistory.tree.create_tree and its helper functions.

Two assumptions were made that you'll likely need to adjust:

1. Import path: assumed create_tree() and its helpers live in
   familyhistory/tree.py. Change the import below if it's elsewhere
   (e.g. familyhistory/services.py, familyhistory/utils.py).

2. Relationship FK field names: assumed the model has FK fields named
   `person` and `related_person` (so the raw id columns are person_id /
   related_person_id, which is what create_tree reads). Adjust the
   .objects.create(...) calls in CreateTreeIntegrationTests if your
   field names differ.

Design notes:

- Most of the logic (_gender_code, _sort_partners, _build_relationship_maps,
  _person_to_node) doesn't actually need the database - it just operates on
  objects with the right attributes. Those tests use SimpleTestCase (which
  forbids DB access, so it'll fail loudly if a test accidentally needs the DB)
  and plain SimpleNamespace stand-ins instead of real model instances.

- CreateTreeIntegrationTests is the only class that hits the database, to
  check the actual query + wiring end-to-end. It patches get_display_name()
  and get_birth_death_date() so these tests don't depend on - or break
  because of - whatever those methods currently do.
"""

from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase

from familyhistory.helpers.tree import (
    _build_relationship_maps,
    _gender_code,
    _person_to_node,
    _sort_partners,
    create_tree,
)
from familyhistory.models import Person, Relationship


class GenderCodeTests(SimpleTestCase):
    def test_male_maps_to_m(self):
        self.assertEqual(_gender_code(SimpleNamespace(gender="male")), "M")

    def test_female_maps_to_f(self):
        self.assertEqual(_gender_code(SimpleNamespace(gender="female")), "F")

    def test_other_value_maps_to_none(self):
        self.assertIsNone(_gender_code(SimpleNamespace(gender="non-binary")))

    def test_blank_value_maps_to_none(self):
        self.assertIsNone(_gender_code(SimpleNamespace(gender="")))


class BuildRelationshipMapsTests(SimpleTestCase):
    @staticmethod
    def _rel(type_, person_id, related_person_id):
        return SimpleNamespace(
            type=type_, person_id=person_id, related_person_id=related_person_id
        )

    def test_father_relationship_populates_parents_and_children(self):
        parents, children, _partners = _build_relationship_maps(
            [self._rel("is_father_of", 1, 2)]
        )
        self.assertEqual(parents[2]["is_father_of"], 1)
        self.assertEqual(children[1], [2])

    def test_mother_relationship_populates_parents_and_children(self):
        parents, children, _partners = _build_relationship_maps(
            [self._rel("is_mother_of", 3, 2)]
        )
        self.assertEqual(parents[2]["is_mother_of"], 3)
        self.assertEqual(children[3], [2])

    def test_married_relationship_is_added_in_both_directions(self):
        rel = self._rel("is_married_to", 1, 2)
        _parents, _children, partners = _build_relationship_maps([rel])
        self.assertEqual(partners[1], [(2, rel)])
        self.assertEqual(partners[2], [(1, rel)])

    def test_in_relationship_with_is_treated_as_partner_too(self):
        rel = self._rel("in_relationship_with", 4, 5)
        _parents, _children, partners = _build_relationship_maps([rel])
        self.assertEqual(partners[4], [(5, rel)])
        self.assertEqual(partners[5], [(4, rel)])

    def test_unrecognised_relationship_type_is_ignored(self):
        parents, children, partners = _build_relationship_maps(
            [self._rel("is_sibling_of", 1, 2)]
        )
        self.assertEqual(parents, {})
        self.assertEqual(children, {})
        self.assertEqual(partners, {})

    def test_multiple_children_accumulate_in_order(self):
        _parents, children, _partners = _build_relationship_maps(
            [self._rel("is_father_of", 1, 2), self._rel("is_father_of", 1, 3)]
        )
        self.assertEqual(children[1], [2, 3])


class SortPartnersTests(SimpleTestCase):
    @staticmethod
    def _rel(start_year=None, start_month=None, start_day=None, end_year=None):
        return SimpleNamespace(
            start_year=start_year,
            start_month=start_month,
            start_day=start_day,
            end_year=end_year,
        )

    def test_current_relationship_sorts_before_ended_ones(self):
        current = self._rel(start_year=2010, end_year=None)
        recently_ended = self._rel(start_year=2000, end_year=2005)
        old = self._rel(start_year=1980, end_year=1990)

        # deliberately out of order, to prove _sort_partners does the work
        partners = {1: [(4, old), (2, current), (3, recently_ended)]}

        _sort_partners(partners)

        self.assertEqual([pid for pid, _rel in partners[1]], [2, 3, 4])

    def test_leaves_a_single_partner_untouched(self):
        rel = self._rel(start_year=1999, end_year=None)
        partners = {1: [(2, rel)]}

        _sort_partners(partners)

        self.assertEqual(partners[1], [(2, rel)])


class PersonToNodeTests(SimpleTestCase):
    @staticmethod
    def _person(**overrides):
        defaults = {
            "id": 1,
            "first_nam": "Ada",
            "birth_surname": "Lovelace",
            "gender": "female",
            "photo": None,
            "get_display_name": lambda: "Ada Lovelace",
            "get_birth_death_date": lambda: "1815-1852",
        }
        defaults.update(overrides)
        return SimpleNamespace(**defaults)

    def test_basic_fields_are_mapped(self):
        person = self._person()
        node = _person_to_node(
            person, start_person_id=99, parents={1: {}}, children={}, partners={}
        )
        self.assertEqual(node["id"], "1")
        self.assertFalse(node["main"])
        self.assertEqual(node["data"]["fn"], "Ada")
        self.assertEqual(node["data"]["ln"], "Lovelace")
        self.assertEqual(node["data"]["label"], "Ada Lovelace")
        self.assertEqual(node["data"]["desc"], "1815-1852")
        self.assertEqual(node["data"]["gender"], "F")
        self.assertIsNone(node["data"]["avatar"])

    def test_main_flag_set_for_the_start_person(self):
        person = self._person(id=7)
        node = _person_to_node(
            person, start_person_id=7, parents={7: {}}, children={}, partners={}
        )
        self.assertTrue(node["main"])

    def test_avatar_uses_photo_url_when_present(self):
        person = self._person(photo=SimpleNamespace(url="/media/ada.jpg"))
        node = _person_to_node(
            person, start_person_id=None, parents={1: {}}, children={}, partners={}
        )
        self.assertEqual(node["data"]["avatar"], "/media/ada.jpg")

    def test_father_and_mother_resolved_from_parents_map(self):
        person = self._person(id=2)
        parents = {2: {"is_father_of": 10, "is_mother_of": 11}}
        node = _person_to_node(
            person, start_person_id=None, parents=parents, children={}, partners={}
        )
        self.assertEqual(node["rels"]["father"], "10")
        self.assertEqual(node["rels"]["mother"], "11")

    def test_missing_parents_become_empty_strings(self):
        person = self._person(id=2)
        node = _person_to_node(
            person, start_person_id=None, parents={2: {}}, children={}, partners={}
        )
        self.assertEqual(node["rels"]["father"], "")
        self.assertEqual(node["rels"]["mother"], "")

    def test_children_and_spouses_are_stringified(self):
        person = self._person(id=1)
        node = _person_to_node(
            person,
            start_person_id=None,
            parents={1: {}},
            children={1: [2, 3]},
            partners={1: [(5, SimpleNamespace())]},
        )
        self.assertEqual(node["rels"]["children"], ["2", "3"])
        self.assertEqual(node["rels"]["spouses"], ["5"])


class CreateTreeIntegrationTests(TestCase):
    """End-to-end tests hitting the real database via create_tree()."""

    def setUp(self):
        display_name_patcher = patch.object(
            Person,
            "get_display_name",
            lambda self: f"{self.first_name} {self.birth_surname}",
        )
        birth_death_patcher = patch.object(
            Person, "get_birth_death_date", lambda self: ""
        )
        self.addCleanup(display_name_patcher.stop)
        self.addCleanup(birth_death_patcher.stop)
        display_name_patcher.start()
        birth_death_patcher.start()

    def test_returns_a_node_for_every_person(self):
        alice = Person.objects.create(
            first_name="Alice", birth_surname="Smith", gender="female"
        )
        bob = Person.objects.create(
            first_name="Bob", birth_surname="Jones", gender="male"
        )

        tree = create_tree(alice.id)

        self.assertEqual(len(tree), 2)
        self.assertEqual({node["id"] for node in tree}, {str(alice.id), str(bob.id)})

    def test_main_person_is_flagged(self):
        alice = Person.objects.create(
            first_name="Alice", birth_surname="Smith", gender="female"
        )
        bob = Person.objects.create(
            first_name="Bob", birth_surname="Jones", gender="male"
        )

        tree = create_tree(bob.id)
        by_id = {node["id"]: node for node in tree}

        self.assertTrue(by_id[str(bob.id)]["main"])
        self.assertFalse(by_id[str(alice.id)]["main"])

    def test_parent_child_relationship_is_reflected_both_ways(self):
        parent = Person.objects.create(
            first_name="Parent", birth_surname="Smith", gender="male"
        )
        child = Person.objects.create(
            first_name="Child", birth_surname="Smith", gender="female"
        )
        Relationship.objects.create(
            person=parent, related_person=child, type="is_father_of"
        )

        tree = create_tree(child.id)
        by_id = {node["id"]: node for node in tree}

        self.assertEqual(by_id[str(child.id)]["rels"]["father"], str(parent.id))
        self.assertEqual(by_id[str(parent.id)]["rels"]["children"], [str(child.id)])

    def test_partner_relationship_is_reflected_both_ways(self):
        sam = Person.objects.create(
            first_name="Sam", birth_surname="Lee", gender="male"
        )
        kim = Person.objects.create(
            first_name="Kim", birth_surname="Lee", gender="female"
        )
        Relationship.objects.create(
            person=sam, related_person=kim, type="is_married_to"
        )

        tree = create_tree(sam.id)
        by_id = {node["id"]: node for node in tree}

        self.assertEqual(by_id[str(sam.id)]["rels"]["spouses"], [str(kim.id)])
        self.assertEqual(by_id[str(kim.id)]["rels"]["spouses"], [str(sam.id)])

    def test_non_family_relationship_types_are_excluded(self):
        sam = Person.objects.create(
            first_name="Sam", birth_surname="Lee", gender="male"
        )
        kim = Person.objects.create(
            first_name="Kim", birth_surname="Lee", gender="female"
        )
        Relationship.objects.create(
            person=sam, related_person=kim, type="is_sibling_of"
        )

        tree = create_tree(sam.id)
        by_id = {node["id"]: node for node in tree}

        self.assertEqual(by_id[str(sam.id)]["rels"]["spouses"], [])
