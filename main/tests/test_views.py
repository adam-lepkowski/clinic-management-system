from unittest.mock import patch, call

from django.contrib.auth.models import User
from django.test import TestCase

from patients.models import Patient
from ..forms import ScheduleSearchForm


class TestScheduleSearchView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test_name",
            email="test@email.com",
            password="test_pw"
        )

    def test_get(self):
        self.client.force_login(self.user)
        response = self.client.get("/schedule/search")
        self.assertIsInstance(response.context["form"], ScheduleSearchForm)
        self.assertTemplateUsed(response, "main/schedule.html")

    def test_ajax_get(self):
        self.client.force_login(self.user)
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

    def test_redirect_when_no_specialty_or_date(self):
        self.client.force_login(self.user)
        response = self.client.get("/schedule/search-results", follow=True)
        self.assertRedirects(response, "/schedule/search")

    def test_post_redirects(self):
        self.client.force_login(self.user)
        data = {
            "hour": "08:30",
            "doctor_id": "1",
            "date": "2023-01-01"
        }
        response = self.client.post(
            "/schedule/search-results",
            data=data,
            follow=True
        )
        self.assertRedirects(response, "/appointment/confirm")

    def test_post_saves_data_to_session(self):
        self.client.force_login(self.user)
        session = self.client.session
        data = {
            "hour": "08:30",
            "doctor_id": "1",
            "date": "2023-01-01"
        }
        self.client.post("/schedule/search-results", data=data, follow=True)
        for key in data:
            self.assertTrue(session[key] == data[key])


class TestAppointmentConfirmView(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_name",
            email="test@email.com",
            password="test_pw"
        )
        self.post_data = {
            "personal_id": "12345678911",
            "purpose": "lorem ipsum"
        }

    def test_get(self):
        self.client.force_login(self.user)
        response = self.client.get("/appointment/confirm")
        self.assertTemplateUsed(response, "main/appointment_confirm.html")

    @patch("main.views.AppointmentConfirmForm.is_valid", return_value=False)
    def test_post_invalid_post_data_returns_same_page(self, mock_is_valid):
        self.client.force_login(self.user)
        response = self.client.post(
            "/appointment/confirm",
            data=self.post_data
        )
        self.assertTemplateUsed(response, "main/appointment_confirm.html")

    @patch("main.views.Patient")
    @patch("main.views.User")
    @patch("main.views.datetime")
    @patch("main.views.Appointment")
    def test_valid_post_data(self, mock_save, mock_datetime,
                             mock_user, mock_patient):
        self.client.force_login(self.user)
        session = self.client.session
        session["hour"] = "08:30"
        session["date"] = "2023-01-01"
        session["doctor_id"] = "1"
        session.save()
        response = self.client.post(
            "/appointment/confirm",
            data=self.post_data,
            follow=True
        )
        self.assertRedirects(response, "/")
