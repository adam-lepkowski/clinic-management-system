from unittest.mock import patch, call

from django.contrib.auth.models import User, Group
from django.test import TestCase
from django.utils import timezone


class TestScheduleSearchView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test_name",
            email="test@email.com",
            password="test_pw"
        )
        self.nurses_group = Group.objects.create(name="nurses")
        self.user.groups.add(self.nurses_group)
        self.client.force_login(self.user)

    def test_get_not_nurse_forbidden(self):
        self.user.groups.remove(self.nurses_group)
        response = self.client.get("/schedule/search")
        self.assertEqual(response.status_code, 403)

    @patch("main.views.ScheduleSearchForm")
    def test_get(self, mock_schedule_form):
        response = self.client.get("/schedule/search")
        self.assertEqual(response.context["form"], mock_schedule_form())
        self.assertTemplateUsed(response, "main/schedule.html")

    def test_ajax_get(self):
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
        self.nurses_group = Group.objects.create(name="nurses")
        self.user.groups.add(self.nurses_group)
        self.client.force_login(self.user)

    def test_get_not_nurse_forbidden(self):
        self.user.groups.remove(self.nurses_group)
        response = self.client.get("/schedule/search-results", data=self.data)
        self.assertEqual(response.status_code, 403)

    @patch("main.views.Schedule.objects.filter")
    def test_get(self, mock_schedule_filter):
        response = self.client.get("/schedule/search-results", data=self.data)
        self.assertTemplateUsed(response, "main/schedule_search_results.html")

    @patch("main.views.Q")
    @patch("main.views.Schedule.objects.filter")
    def test_schedule_q_calls_emp(self, mock_schedule_filter, mock_views_q):
        self.client.get('/schedule/search-results', data=self.data)
        expected_q_calls = [
            call(employee__groups__id="1"),
            call(employee__id="1"),
            call(date="2023-01-01")]
        self.assertEqual(mock_views_q.call_args_list, expected_q_calls)

    @patch("main.views.Q")
    @patch("main.views.Schedule.objects.filter")
    def test_schedule_q_calls_no_emp(self, mock_schedule_filter, mock_views_q):
        self.data["employee"] = ""
        self.client.get('/schedule/search-results', data=self.data)
        expected_q_calls = [
            call(employee__groups__id="1"),
            call(date="2023-01-01")]
        self.assertEqual(mock_views_q.call_args_list, expected_q_calls)

    def test_redirect_when_no_specialty_or_date(self):
        response = self.client.get("/schedule/search-results", follow=True)
        self.assertRedirects(response, "/schedule/search")

    def test_post_redirects(self):
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
        self.nurses_group = Group.objects.create(name="nurses")
        self.user.groups.add(self.nurses_group)
        self.client.force_login(self.user)

    def test_get_not_nurse_forbidden(self):
        self.user.groups.remove(self.nurses_group)
        response = self.client.get("/appointment/confirm")
        self.assertEqual(response.status_code, 403)

    def test_get_valid_session(self):
        session = self.client.session
        session["hour"] = "08:30"
        session["date"] = "2023-01-01"
        session["doctor_id"] = "1"
        session.save()
        response = self.client.get("/appointment/confirm")
        self.assertTemplateUsed(response, "main/appointment_confirm.html")

    def test_get_invalid_session_redirects_to_schedule_form(self):
        response = self.client.get("/appointment/confirm")
        self.assertRedirects(response, "/schedule/search")

    @patch("main.views.AppointmentConfirmForm.is_valid", return_value=False)
    def test_post_invalid_form_returns_same_page(self, mock_is_valid):
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

    @patch("main.views.Patient")
    @patch("main.views.User")
    @patch("main.views.datetime")
    @patch("main.views.Appointment")
    def test_valid_post_resets_session(self, mock_save, mock_datetime,
                                       mock_user, mock_patient):
        session = self.client.session
        session["hour"] = "08:30"
        session["date"] = "2023-01-01"
        session["doctor_id"] = "1"
        session.save()
        self.client.post("/appointment/confirm", data=self.post_data)
        self.assertIsNone(self.client.session["hour"])
        self.assertIsNone(self.client.session["date"])
        self.assertIsNone(self.client.session["doctor_id"])


class TestMainView(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_name",
            email="test@email.com",
            password="test_pw"
        )
        self.physicians_group = Group.objects.create(name="physicians")
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
        self.client.force_login(self.user)

    def test_get_no_appointment_without_form_in_context(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "main/index.html")
        self.assertIsNone(response.context.get("form"))

    @patch("main.views.get_next_appointment", return_value=True)
    @patch("main.views.AppointmentModelForm")
    @patch("main.views.Appointment")
    def test_get_appointment_form_in_context(
            self, mock_appointment, mock_appointment_form,
            mock_next_appointment):
        self.user.groups.add(self.physicians_group)
        response = self.client.get("/")
        self.assertTemplateUsed(response, "main/index.html")
        self.assertIsNotNone(response.context.get("form"))

    @patch("main.views.get_next_appointment", return_value=True)
    @patch("main.views.Appointment")
    @patch("main.views.AppointmentModelForm")
    def test_post_valid_data_with_next_appointment(
            self, mock_appointment_form, mock_appointment,
            mock_next_appointment):
        response = self.client.post("/", data=self.data)
        self.assertTemplateUsed(response, "main/index.html")
        self.assertIsNotNone(response.context.get("form"))

    @patch("main.views.get_next_appointment", return_value=False)
    @patch("main.views.Appointment")
    @patch("main.views.AppointmentModelForm")
    def test_post_valid_data_without_next_appointment(
            self, mock_appointment_form, mock_appointment,
            mock_next_appointment):
        response = self.client.post("/", data=self.data)
        self.assertTemplateUsed(response, "main/index.html")
        self.assertIsNone(response.context.get("form"))

    @patch("main.views.Appointment")
    @patch("main.views.AppointmentModelForm.is_valid")
    def test_post_invalid_data(self, mock_appointment_form, mock_appointment):
        mock_appointment_form.return_value = False
        response = self.client.post("/", data=self.data)
        self.assertTemplateUsed(response, "main/index.html")
        self.assertIsNotNone(response.context.get("form"))

    @patch("main.views.Appointment")
    def test_get_nurse(self, mock_appointment):
        nurses_group = Group.objects.create(name="nurses")
        self.user.groups.add(nurses_group)
        response = self.client.get("/")
        mock_returned_appointments = mock_appointment.objects.filter().order_by
        mock_returned_appointments.assert_called_once()
        self.assertEqual(
            response.context["appointments"],
            mock_returned_appointments()
        )
        self.assertTemplateUsed(response, "main/index.html")

    @patch("main.views.AppointmentModelForm")
    @patch("main.views.get_next_appointment")
    def test_get_doctor(self, mock_get_appointment, mock_appointment_form):
        self.user.groups.add(self.physicians_group)
        response = self.client.get("/")
        self.assertEqual(
            response.context["form"],
            mock_appointment_form()
        )
        self.assertTemplateUsed(response, "main/index.html")


class TestAppointmentView(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_name",
            email="test@email.com",
            password="test_pw"
        )
        self.client.force_login(self.user)

    def test_get_no_appointment(self):
        response = self.client.get("/appointment/1")
        self.assertTemplateUsed(response, "404.html")

    @patch("main.views.Appointment")
    @patch("main.views.AppointmentModelForm")
    @patch("main.views.get_object_or_404")
    def test_get(self, mock_404, mock_appointment_form, mock_appointment):
        response = self.client.get("/appointment/1")
        self.assertTemplateUsed(response, "main/appointment.html")

    @patch("main.views.AppointmentModelForm")
    @patch("main.views.get_object_or_404")
    def test_post_valid_redirects(self, mock_404, mock_appointment_form):
        response = self.client.post(
            "/appointment/1", data={"data": "data"}, follow=True
        )
        self.assertRedirects(response, "/appointment/1")

    @patch("main.views.AppointmentModelForm.is_valid", return_value=False)
    @patch("main.views.get_object_or_404")
    def test_post_invalid_returns_same_page(self, mock_404, mock_is_valid):
        response = self.client.post(
            "/appointment/1", data={"data": "data"}, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main/appointment.html")


class TestAppointmentDeleteView(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_name",
            email="test@email.com",
            password="test_pw"
        )
        self.nurses_group = Group.objects.create(name="nurses")
        self.user.groups.add(self.nurses_group)
        self.client.force_login(self.user)

    def test_get_not_nurse_forbidden(self):
        self.user.groups.remove(self.nurses_group)
        response = self.client.get("/appointment/confirm")
        self.assertEqual(response.status_code, 403)

    def test_get_no_appointment(self):
        response = self.client.get("/appointment/delete/1")
        self.assertTemplateUsed(response, "404.html")

    @patch("django.utils.dateformat.DateFormat")
    @patch("main.views.get_object_or_404")
    def test_get(self, mock_404, mock_dateformat):
        response = self.client.get("/appointment/delete/1")
        self.assertTemplateUsed(response, "main/appointment_delete.html")

    def test_post_no_appointment(self):
        response = self.client.post(
            "/appointment/delete/1", data={"data": "data"}
        )
        self.assertTemplateUsed(response, "404.html")

    @patch("main.views.Appointment")
    @patch("main.views.get_object_or_404")
    def test_post_appointment_deleted(self, mock_404, mock_appointment):
        self.client.post("/appointment/delete/1", data={"data": "data"})
        mock_404.assert_called_with(mock_appointment, id=1)
        mock_404().delete.assert_called_once()

    @patch("main.views.Appointment")
    @patch("main.views.get_object_or_404")
    def test_post_appointment_deleted(self, mock_404, mock_appointment):
        response = self.client.post(
            "/appointment/delete/1", data={"data": "data"}
        )
        self.assertRedirects(response, "/")
