from django.test import TestCase
from django.contrib.auth.models import User, Group

from ..models import Schedule
from ..forms import ScheduleSearchForm


class TestScheduleSearchView(TestCase):

    def test_get(self):
        response = self.client.get("/schedule/search")
        self.assertIsInstance(response.context["form"], ScheduleSearchForm)
        self.assertTemplateUsed(response, "main/schedule.html")

    def test_ajax_get(self):
        response = self.client.get(
            "/schedule/search", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertTemplateUsed(response, "main/includes/specialists.html")


class TestScheduleListView(TestCase):

    def setUp(self):
        group = Group.objects.create(name="TestGroup")
        group2 = Group.objects.create(name="TestGroup2")
        user = User.objects.create(
            username="TestUser",
            first_name="Teston",
            last_name="Testingly")
        user.groups.add(group)
        user2 = User.objects.create(
            username="TestUserTheSecond",
            first_name="Secondton",
            last_name="Testerly-Hills")
        user2.groups.add(group2)
        self.schedule = Schedule.objects.create(
            date="2023-01-01",
            start="08:00",
            end="16:00",
            employee=user)
        Schedule.objects.create(
            date="2023-01-01",
            start="08:00",
            end="16:00",
            employee=user2)
        self.data = {
            "specialties": 1,
            "date": "2023-01-01",
            "employee": 1
        }

    def test_get(self):
        response = self.client.get('/schedule/search-results', data=self.data)
        self.assertTemplateUsed(response, "main/schedule_search_results.html")

    def test_response_queryset(self):
        response = self.client.get('/schedule/search-results', data=self.data)
        self.assertEqual(response.context["dates"][0], self.schedule)
        self.assertEqual(len(response.context["dates"]), 1)