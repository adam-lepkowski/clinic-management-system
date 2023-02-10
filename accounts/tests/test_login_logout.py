from django.test import TestCase
from django.contrib.auth.models import User


class TestLogin(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_name",
            email="test@email.com",
            password="test_pw")
    
    def test_login(self):
        self.client.login(username="test_name", password="test_pw")
        response = self.client.get("/account/login")
        self.assertRedirects(response, "/")


class TestLogout(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_name",
            email="test@email.com",
            password="test_pw")
    
    def test_logout(self):
        self.client.login(username="test_name", password="test_pw")
        response = self.client.post("/account/logout")
        self.assertRedirects(response, "/account/login")