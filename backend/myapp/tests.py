from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from myapp.models import UserProfile


class ViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="bob", password="pass123")
        UserProfile.objects.create(user=self.user)

    def test_index_loads(self):
        response = self.client.get(reverse("myapp:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Olympic Games 2026")

    def test_registration_creates_user_and_profile(self):
        self.client.post(reverse("myapp:register"), {
            "username": "newbie",
            "email": "n@example.com",
            "password": "secret123",
            "confirm_password": "secret123",
            "role": "spectator",
        })
        self.assertTrue(User.objects.filter(username="newbie").exists())
        self.assertTrue(UserProfile.objects.filter(user__username="newbie").exists())
