"""Build the family-chart.js node graph from Person/Relationship data."""

from collections import defaultdict

from familyhistory.models import Person, Relationship

PARENT_TYPES = ("is_father_of", "is_mother_of")
PARTNER_TYPES = ("is_married_to", "in_relationship_with")


def _build_relationship_maps(relationships):
    """Build parent/child/partner lookup maps from a list of relationships.

    Args:
        relationships: Iterable of `Relationship` instances, restricted to
            parent and partner types.

    Returns:
        A 3-tuple of ``(parents, children, partners)`` dicts keyed by
        person ID: ``parents`` maps to a ``{relationship_type: person_id}``
        dict, ``children`` to a list of child IDs, and ``partners`` to a
        list of ``(partner_id, relationship)`` tuples.
    """
    parents = defaultdict(dict)
    children = defaultdict(list)
    partners = defaultdict(list)

    for rel in relationships:
        if rel.type in PARENT_TYPES:
            parents[rel.related_person_id][rel.type] = rel.person_id
            children[rel.person_id].append(rel.related_person_id)
        elif rel.type in PARTNER_TYPES:
            partners[rel.person_id].append((rel.related_person_id, rel))
            partners[rel.related_person_id].append((rel.person_id, rel))

    return parents, children, partners


def _partner_sort_key(entry):
    """Sort key ordering current/most recent partner relationships first.

    Args:
        entry: A ``(partner_id, relationship)`` tuple as stored in the
            partners map built by `_build_relationship_maps`.

    Returns:
        A tuple usable as a `list.sort` key.
    """
    _pid, rel = entry
    return (
        rel.end_year is None,
        rel.start_year or 9999,
        rel.start_month or 12,
        rel.start_day or 31,
    )


def _sort_partners(partners):
    """Sort each person's partner list, most recent/current relationship first.

    Args:
        partners: The partners map built by `_build_relationship_maps`,
            mutated in place.
    """
    for plist in partners.values():
        plist.sort(key=_partner_sort_key, reverse=True)


def _gender_code(person):
    """Map a `Person.gender` value to the single-letter code family-chart.js expects.

    Args:
        person: The `Person` whose gender is being encoded.

    Returns:
        ``"M"``, ``"F"``, or ``None`` if the gender is unset/unrecognised.
    """
    if person.gender == "male":
        return "M"
    if person.gender == "female":
        return "F"
    return None


def _person_to_node(person, start_person_id, parents, children, partners):
    """Build the f3/d3 tree node dict for a single person.

    Args:
        person: The `Person` to render as a node.
        start_person_id: ID of the person the tree is rooted on, used to
            flag the node as `"main"`.
        parents: Parents map from `_build_relationship_maps`.
        children: Children map from `_build_relationship_maps`.
        partners: Partners map from `_build_relationship_maps`.

    Returns:
        A dict in the shape family-chart.js expects, with `id`, `main`,
        `data`, and `rels` keys.
    """
    father_id = parents[person.id].get("is_father_of")
    mother_id = parents[person.id].get("is_mother_of")

    return {
        "id": str(person.id),
        "main": start_person_id == person.id,
        "data": {
            "fn": person.first_name,
            "ln": person.birth_surname,
            "label": person.get_display_name(),
            "desc": person.get_birth_death_date(),
            "avatar": person.photo.url if person.photo else None,
            "gender": _gender_code(person),
        },
        "rels": {
            "father": str(father_id) if father_id else "",
            "mother": str(mother_id) if mother_id else "",
            "spouses": [str(pid) for pid, _rel in partners.get(person.id, [])],
            "children": [str(cid) for cid in children.get(person.id, [])],
        },
    }


def create_tree(start_person_id: int):
    """Build the full family tree as a list of family-chart.js node dicts.

    Loads all people and parent/partner relationships in bulk and derives
    the tree structure from those `Relationship` edges - nothing is read
    from `TreeCache` here, so this always reflects live data.

    Args:
        start_person_id (int): ID of the person the tree should be rooted/centred
            on; that person's node is flagged as `"main"`.

    Returns:
        A list of node dicts, one per `Person`, in the shape family-chart.js
        expects.
    """
    people = Person.objects.all()
    relationships = Relationship.objects.filter(
        type__in=[*PARENT_TYPES, *PARTNER_TYPES]
    ).only(
        "person_id",
        "related_person_id",
        "type",
        "end_year",
        "start_year",
        "start_month",
        "start_day",
    )

    parents, children, partners = _build_relationship_maps(relationships)
    _sort_partners(partners)

    return [
        _person_to_node(person, start_person_id, parents, children, partners)
        for person in people
    ]
