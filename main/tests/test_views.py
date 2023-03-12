from unittest.mock import patch, call, Mock

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

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

    def test_get_valid_session(self):
        self.client.force_login(self.user)
        session = self.client.session
        session["hour"] = "08:30"
        session["date"] = "2023-01-01"
        session["doctor_id"] = "1"
        session.save()
        response = self.client.get("/appointment/confirm")
        self.assertTemplateUsed(response, "main/appointment_confirm.html")

    def test_get_invalid_session_redirects_to_schedule_form(self):
        self.client.force_login(self.user)
        response = self.client.get("/appointment/confirm")
        self.assertRedirects(response, "/schedule/search")

    @patch("main.views.AppointmentConfirmForm.is_valid", return_value=False)
    def test_post_invalid_form_returns_same_page(self, mock_is_valid):
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

    def test_invalid_patient_id_returns_same_page_with_error(self):
        self.client.force_login(self.user)
        response = self.client.post(
            "/appointment/confirm",
            data=self.post_data
        )
        self.assertTemplateUsed(response, "main/appointment_confirm.html")
        self.assertEqual(response.context["error"], "Invalid patient id")

    @patch("main.views.Patient")
    @patch("main.views.AppointmentConfirmForm")
    def test_invalid_session_data_returns_same_page_with_error(
            self, mock_appointment_form, mock_patient):
        self.client.force_login(self.user)
        response = self.client.post(
            "/appointment/confirm",
            data=self.post_data
        )
        self.assertTemplateUsed(response, "main/appointment_confirm.html")
        self.assertEqual(
            response.context["error"],
            "Fill out schedule form first."
        )

    @patch("main.views.Patient")
    @patch("main.views.AppointmentConfirmForm")
    def test_invalid_doctor_id_returns_same_page_with_error(
            self, mock_appointment_form, mock_patient):
        self.client.force_login(self.user)
        session = self.client.session
        session["hour"] = "08:30"
        session["date"] = "2023-01-01"
        session["doctor_id"] = "10"
        session.save()
        response = self.client.post(
            "/appointment/confirm",
            data=self.post_data
        )
        self.assertTemplateUsed(response, "main/appointment_confirm.html")
        self.assertEqual(
            response.context["error"],
            "Invalid doctor ID"
        )


class TestMainView(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_name",
            email="test@email.com",
            password="test_pw"
        )
        self.data = {
            "datetime": timezone.now(),
            "patient": "1",
            "doctor": "1",
            "purpose": "Toothache",
            "examination": "",
            "diagnosis": "",
            "advice": "",
            "prescription": "",
            "took_place": True
        }

    def test_get_no_appointment_without_form_in_context(self):
        self.client.force_login(self.user)
        response = self.client.get("/")
        self.assertTemplateUsed(response, "main/index.html")
        self.assertIsNone(response.context.get("form"))

    @patch("main.views.get_next_appointment", return_value=True)
    @patch("main.views.AppointmentModelForm")
    @patch("main.views.Appointment")
    def test_get_appointment_form_in_context(
            self, mock_appointment, mock_appointment_form,
            mock_next_appointment):
        self.client.force_login(self.user)
        response = self.client.get("/")
        self.assertTemplateUsed(response, "main/index.html")
        self.assertIsNotNone(response.context.get("form"))

    @patch("main.views.get_next_appointment", return_value=True)
    @patch("main.views.Appointment")
    @patch("main.views.AppointmentModelForm")
    def test_post_valid_data_with_next_appointment(
            self, mock_appointment_form, mock_appointment,
            mock_next_appointment):
        self.client.force_login(self.user)
        response = self.client.post("/", data=self.data)
        self.assertTemplateUsed(response, "main/index.html")
        self.assertIsNotNone(response.context.get("form"))

    @patch("main.views.get_next_appointment", return_value=False)
    @patch("main.views.Appointment")
    @patch("main.views.AppointmentModelForm")
    def test_post_valid_data_without_next_appointment(
            self, mock_appointment_form, mock_appointment,
            mock_next_appointment):
        self.client.force_login(self.user)
        response = self.client.post("/", data=self.data)
        self.assertTemplateUsed(response, "main/index.html")
        self.assertIsNone(response.context.get("form"))

    @patch("main.views.Appointment")
    @patch("main.views.AppointmentModelForm.is_valid")
    def test_post_invalid_data(self, mock_appointment_form, mock_appointment):
        self.client.force_login(self.user)
        mock_appointment_form.return_value = False
        response = self.client.post("/", data=self.data)
        self.assertTemplateUsed(response, "main/index.html")
        self.assertIsNotNone(response.context.get("form"))


class TestAppointmentView(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_name",
            email="test@email.com",
            password="test_pw"
        )

    def test_get_no_appointment(self):
        self.client.force_login(self.user)
        response = self.client.get("/appointment/1")
        self.assertTemplateUsed(response, "404.html")

    @patch("main.views.Appointment")
    @patch("main.views.AppointmentModelForm")
    @patch("main.views.get_object_or_404")
    def test_get(self, mock_404, mock_appointment_form, mock_appointment):
        self.client.force_login(self.user)
        response = self.client.get("/appointment/1")
        self.assertTemplateUsed(response, "main/appointment.html")
