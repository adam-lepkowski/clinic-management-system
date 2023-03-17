from unittest.mock import patch

from django.contrib.auth.models import User, Group
from django.test import TestCase


class TestRegistrationView(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_name",
            email="test@email.com",
            password="test_pw"
        )
        nurses_group = Group.objects.create(name="nurses")
        self.user.groups.add(nurses_group)

    def test_get_redirects_anonymous_user_to_login(self):
        response = self.client.get("/patient/register", follow=True)
        self.assertRedirects(response, "/account/login?next=/patient/register")

    @patch("patients.views.AddressForm")
    @patch("patients.views.PatientForm")
    def test_post_redirects_anonymous_user_to_login(
            self, mock_patient_form, mock_address_form):
        response = self.client.post("/patient/register", follow=True)
        self.assertRedirects(response, "/account/login?next=/patient/register")

    @patch("patients.views.AddressForm")
    @patch("patients.views.PatientForm")
    def test_registration_valid_forms(
            self, mock_patient_form, mock_address_form):
        self.client.force_login(self.user)
        response = self.client.post("/patient/register", follow=True)
        mock_patient_form().save.assert_called_once()
        mock_address_form().save.assert_called_once()
        self.assertRedirects(response, "/patient/registered")

    @patch("patients.views.AddressForm")
    @patch("patients.views.PatientForm")
    def test_registration_valid_forms_sets_session_attr(
            self, mock_patient_form, mock_address_form):
        self.client.force_login(self.user)
        self.client.post("/patient/register")
        result = self.client.session.get("patient-registered", False)
        self.assertTrue(result)

    @patch("patients.views.AddressForm.is_valid", return_value=False)
    @patch("patients.views.PatientForm")
    def test_registration_invalid_address_form(
            self, mock_patient_form, mock_address_is_valid):
        self.client.force_login(self.user)
        response = self.client.post("/patient/register", follow=True)
        self.assertTemplateNotUsed(response, "/patient/registered")
        self.assertEqual(len(response.redirect_chain), 0)

    @patch("patients.views.AddressForm")
    @patch("patients.views.PatientForm.is_valid", return_value=False)
    def test_registration_invalid_patient_form(
            self, mock_patient_is_valid, mock_address_form):
        self.client.force_login(self.user)
        response = self.client.post("/patient/register", follow=True)
        self.assertTemplateNotUsed(response, "/patient/registered")
        self.assertEqual(len(response.redirect_chain), 0)


class TestSuccessRegistrationView(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_name",
            email="test@email.com",
            password="test_pw"
        )
        nurses_group = Group.objects.create(name="nurses")
        self.user.groups.add(nurses_group)

    def test_redirect_if_no_form_submitted(self):
        self.client.force_login(self.user)
        response = self.client.get("/patient/registered", follow=True)
        self.assertFalse(self.client.session.get("patient-registered", False))
        self.assertRedirects(response, "/patient/register")


class TestPatientView(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_name",
            email="test@email.com",
            password="test_pw"
        )

    def test_get_redirects_anonymous_user_to_login(self):
        response = self.client.get("/patient/1", follow=True)
        self.assertRedirects(response, "/account/login?next=/patient/1")

    def test_post_redirects_anonymous_user_to_login(self):
        response = self.client.post("/patient/1", follow=True)
        self.assertRedirects(response, "/account/login?next=/patient/1")

    @patch("patients.views.get_object_or_404")
    @patch("patients.views.Appointment")
    @patch("patients.views.AddressForm")
    @patch("patients.views.PatientForm")
    def test_get_valid_patient_id(
            self, mock_patient_form, mock_address_form,
            mock_appointment, mock_404):
        self.client.force_login(self.user)
        response = self.client.get("/patient/1")
        self.assertTemplateUsed(response, "patients/patient.html")

    def test_get_invalid_patient_id(self):
        self.client.force_login(self.user)
        response = self.client.get("/patient/2")
        self.assertTemplateUsed(response, "404.html")

    @patch("patients.views.get_object_or_404")
    @patch("patients.views.Appointment")
    @patch("patients.views.AddressForm")
    @patch("patients.views.PatientForm")
    def test_post_data_changed(
            self, mock_patient_form, mock_address_form,
            mock_appointment, mock_404):
        self.client.force_login(self.user)
        response = self.client.post("/patient/1")
        mock_patient_form().save.assert_called_once()
        mock_address_form().save.assert_called_once()
        self.assertRedirects(response, "/patient/1")

    @patch("patients.views.get_object_or_404")
    @patch("patients.views.AddressForm.changed_data", return_value=[])
    @patch("patients.views.PatientForm.changed_data", return_value=[])
    def test_post_data_not_changed(
            self, mock_patient_changed, mock_address_changed, mock_404):
        self.client.force_login(self.user)
        response = self.client.post("/patient/1", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.redirect_chain), 0)


class TestSearchResultsView(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_name",
            email="test@email.com",
            password="test_pw"
        )

    def test_get_redirects_anonymous_user_to_login(self):
        response = self.client.get(
            "/patient/search-results?query=test",
            follow=True
        )
        self.assertRedirects(
            response,
            "/account/login?next=/patient/search-results?query=test"
        )

    def test_search_result_view(self):
        self.client.force_login(self.user)
        response = self.client.get("/patient/search-results?query=test")
        self.assertTemplateUsed(response, "patients/search_results.html")

    def test_no_search_data_raises_404(self):
        self.client.force_login(self.user)
        response = self.client.get("/patient/search-results")
        self.assertTemplateUsed(response, "404.html")
