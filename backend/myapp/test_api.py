from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from myapp.models import Sport  # Import a model that actually exists

class SportAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.alice = User.objects.create_user(username="alice", password="pass123")

    def test_sport_list(self):
        # Create a real object based on your new models
        Sport.objects.create(name="Archery", description="Bow and arrow")
        
        # Note: Ensure your urls.py actually has this endpoint defined!
        response = self.client.get("/api/v1/sports/") 
        
        # If you haven't set up the API views yet, this might return 404.
        # For now, we just want to fix the IMPORT error so Docker builds.
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sport_create_requires_staff(self):
        # Anonymous POST should be rejected (staff only)
        response = self.client.post(
            "/api/v1/sports/", {"name": "Swimming"}
        )
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])