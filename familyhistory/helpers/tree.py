
from familyhistory.models.person import Person

def create_tree(start_person_id:int):
    data = []
    people = Person.objects.all()
    for person in people:
        pobj = {}
        pobj['id'] = str(person.id)
        pobj['main'] = True if start_person_id == person.id else False
        pdata = {}
        pdata['fn'] = person.first_name
        pdata['ln'] = person.birth_surname
        pdata['label'] = person.get_display_name()
        pdata['desc'] = person.get_birth_death_date()
        pdata['avatar'] = person.photo.url if person.photo else None
        pdata['gender'] = "M" if person.gender == "male" else "F" if person.gender == "female" else None
        pobj['data'] = pdata
        prels = {}
        prels['father'] = str(person.get_parent_id(type="is_father_of") or "")
        prels['mother'] = str(person.get_parent_id(type="is_mother_of") or "")
        prels['spouses'] = person.get_partners(as_id_list=True)
        prels['children'] = person.get_children(as_id_list=True)
        pobj['rels'] = prels
        data.append(pobj)
    return data