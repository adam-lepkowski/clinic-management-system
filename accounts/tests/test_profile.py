from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase


TEST_USER = {
    "username": "test_name",
    "email": "test@email.com",
    "password": "test_pw"
}


class TestProfileView(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_name",
            email="test@email.com",
            password="test_pw"
        )

    def test_profile_anonymous_user_redirect(self):
        response = self.client.get("/account/")
        self.assertRedirects(response, "/account/login?next=/account/")

    def test_profile_logged_in(self):
        self.client.login(username="test_name", password="test_pw")
        response = self.client.get("/account/")
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "accounts/profile.html")