from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.http import JsonResponse
from .models import Event

class EventTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client = APIClient()

        # Obtain token and set credentials
        response = self.client.post('/api/token/', {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 200)
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # Create a test event
        self.event = Event.objects.create(
            author=self.user,
            title="Test Event",
            date="2025-04-01",
            start_time="10:00",
            end_time="12:00",
            note="Test Note"
        )

    def test_authenticated_user_can_view_events(self):
        response = self.client.get("/api/event/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Test Event")

    def test_authenticated_user_can_create_event(self):
        new_event = {
            "title": "New Event",
            "date": "2025-04-02",
            "start_time": "14:00",
            "end_time": "16:00",
        }
        response = self.client.post("/api/event/", new_event)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Event.objects.count(), 2)

    def test_authenticated_user_can_edit_event(self):
        updated_event = {
            "title": "Updated Event",
            "date": "2025-04-01",
            "start_time": "11:00",
            "end_time": "13:00",
            "note": "Updated Note"
        }
        response = self.client.patch(f"/api/event/update/{self.event.id}/", updated_event)
        self.assertEqual(response.status_code, 200)
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, "Updated Event")
        self.assertEqual(self.event.note, "Updated Note")

    def test_authenticated_user_can_delete_event(self):
        response = self.client.delete(f"/api/event/delete/{self.event.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Event.objects.count(), 0)

    def test_unauthenticated_user_cannot_access_events(self):
        self.client.logout()
        response = self.client.get("/api/event/")
        self.assertEqual(response.status_code, 401)

    def test_authenticated_user_can_communicate_with_assistant(self):
        response = self.client.get("/api/assistant/chat/?message=Hello")
        self.assertEqual(response.status_code, 200)

