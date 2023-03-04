from unittest.mock import patch, call

from django.contrib.auth.models import User
from django.test import TestCase

from ..forms import ScheduleSearchForm


class TestScheduleSearchView(TestCase):
    def setUp(self):
        User.objects.create_user(
            username="test_name",
            email="test@email.com",
            password="test_pw"
        )

    def test_get(self):
        self.client.login(username="test_name", password="test_pw")
        response = self.client.get("/schedule/search")
        self.assertIsInstance(response.context["form"], ScheduleSearchForm)
        self.assertTemplateUsed(response, "main/schedule.html")

    def test_ajax_get(self):
        self.client.login(username="test_name", password="test_pw")
        response = self.client.get(
            "/schedule/search",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertTemplateUsed(response, "main/includes/specialists.html")


class TestScheduleListView(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_name",
            email="test@email.com",
            password="test_pw"
        )
        self.data = {
            "specialties": 1,
            "date": "2023-01-01",
            "employee": 1
        }

    @patch("main.views.Schedule.objects.filter")
    def test_get(self, mock_schedule_filter):
        self.client.force_login(self.user)
        response = self.client.get('/schedule/search-results', data=self.data)
        self.assertTemplateUsed(response, "main/schedule_search_results.html")

    @patch("main.views.Q")
    @patch("main.views.Schedule.objects.filter")
    def test_schedule_q_calls_emp(self, mock_schedule_filter, mock_views_q):
        self.client.force_login(self.user)
        self.client.get('/schedule/search-results', data=self.data)
        expected_q_calls = [
            call(employee__groups__id="1"),
            call(employee__id="1"),
            call(date="2023-01-01")]
        self.assertEqual(mock_views_q.call_args_list, expected_q_calls)

    @patch("main.views.Q")
    @patch("main.views.Schedule.objects.filter")
    def test_schedule_q_calls_no_emp(self, mock_schedule_filter, mock_views_q):
        self.client.force_login(self.user)
        self.data["employee"] = ""
        self.client.get('/schedule/search-results', data=self.data)
        expected_q_calls = [
            call(employee__groups__id="1"),
            call(date="2023-01-01")]
        self.assertEqual(mock_views_q.call_args_list, expected_q_calls)
