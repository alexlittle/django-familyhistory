from collections import defaultdict

from familyhistory.models import Person, Relationship


def create_tree(start_person_id: int):
    people = Person.objects.all()

    relationships = Relationship.objects.filter(
        type__in=[
            "is_father_of",
            "is_mother_of",
            "is_married_to",
            "in_relationship_with",
        ]
    ).only(
        "person_id",
        "related_person_id",
        "type",
        "end_year",
        "start_year",
        "start_month",
        "start_day",
    )

    parents = defaultdict(
        dict
    )  # child_id -> {"is_father_of": parent_id, "is_mother_of": parent_id}
    children = defaultdict(list)  # parent_id -> [child_id, ...]
    partners = defaultdict(list)  # person_id -> [(partner_id, relationship), ...]

    for rel in relationships:
        if rel.type in ("is_father_of", "is_mother_of"):
            parents[rel.related_person_id][rel.type] = rel.person_id
            children[rel.person_id].append(rel.related_person_id)
        elif rel.type in ("is_married_to", "in_relationship_with"):
            partners[rel.person_id].append((rel.related_person_id, rel))
            partners[rel.related_person_id].append((rel.person_id, rel))

    for plist in partners.values():
        plist.sort(
            key=lambda x: (
                x[1].end_year is None,
                x[1].start_year or 9999,
                x[1].start_month or 12,
                x[1].start_day or 31,
            ),
            reverse=True,
        )

    data = []
    for person in people:
        pobj = {}
        pobj["id"] = str(person.id)
        pobj["main"] = start_person_id == person.id

        pdata = {
            "fn": person.first_name,
            "ln": person.birth_surname,
            "label": person.get_display_name(),
            "desc": person.get_birth_death_date(),
            "avatar": person.photo.url if person.photo else None,
        }
        if person.gender == "male":
            pdata["gender"] = "M"
        elif person.gender == "female":
            pdata["gender"] = "F"
        else:
            pdata["gender"] = None
        pobj["data"] = pdata

        father_id = parents[person.id].get("is_father_of")
        mother_id = parents[person.id].get("is_mother_of")
        pobj["rels"] = {
            "father": str(father_id) if father_id else "",
            "mother": str(mother_id) if mother_id else "",
            "spouses": [str(pid) for pid, _rel in partners.get(person.id, [])],
            "children": [str(cid) for cid in children.get(person.id, [])],
        }
        data.append(pobj)

    return data
