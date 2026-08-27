from django.test import TestCase
from django.urls import reverse

from familyhistory.models import Document, Event
from tests.familyhistory.views.helpers import make_person


class PersonViewTests(TestCase):
    def test_renders_existing_person(self):
        person = make_person(first_name="Ada", birth_surname="Lovelace")

        response = self.client.get(
            reverse("fh:person_detail", kwargs={"person_id": person.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "fh/person.html")
        self.assertEqual(response.context["person"], person)

    def test_missing_person_returns_404(self):
        response = self.client.get(
            reverse("fh:person_detail", kwargs={"person_id": 999999})
        )
        self.assertEqual(response.status_code, 404)

    def test_related_events_and_documents_are_reachable(self):
        person = make_person(first_name="Ada", birth_surname="Lovelace")
        event = Event.objects.create(title="Christening")
        event.involved.add(person)
        document = Document.objects.create(
            title="Birth certificate", type="birth_certificate"
        )
        document.person_involved.add(person)

        response = self.client.get(
            reverse("fh:person_detail", kwargs={"person_id": person.id})
        )

        fetched = response.context["person"]
        self.assertEqual(list(fetched.events_involved.all()), [event])
        self.assertEqual(list(fetched.document_people.all()), [document])
