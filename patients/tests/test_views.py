from django.contrib.auth.models import User
from django.test import TestCase

from ..models import Patient, Address


class TestRegistrationView(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_name",
            email="test@email.com",
            password="test_pw"
        )
        self.address = {
            "address-street": "Test Lane",
            "address-number": "12a",
            "address-apartment": "123",
            "address-zip_code": "00-000",
            "address-city": "Testington",
            "address-country": "Republic of Testland"
        }
        self.patient = {
            "patient-first_name": "Johnny",
            "patient-last_name": "Test",
            "patient-date_of_birth": "2022-12-12",
            "patient-personal_id": "12345678911",
            "patient-email": "email@email.com",
            "patient-phone": "0123456789"
        }

    def test_get_redirects_anonymous_user_to_login(self):
        response = self.client.get("/patient/register", follow=True)
        self.assertRedirects(response, "/account/login?next=/patient/register")

    def test_post_redirects_anonymous_user_to_login(self):
        data = self.address | self.patient
        response = self.client.post("/patient/register", data, follow=True)
        self.assertRedirects(response, "/account/login?next=/patient/register")

    def test_registration_valid_forms(self):
        self.client.login(username="test_name", password="test_pw")
        data = self.address | self.patient
        response = self.client.post("/patient/register", data, follow=True)
        self.assertRedirects(response, "/patient/registered")

    def test_registration_valid_forms_sets_session_attr(self):
        self.client.login(username="test_name", password="test_pw")
        data = self.address | self.patient
        self.client.post("/patient/register", data)
        result = self.client.session.get("patient-registered", False)
        self.assertTrue(result)

    def test_registration_invalid_address_form(self):
        self.client.login(username="test_name", password="test_pw")
        self.address["address-city"] = ""
        data = self.address | self.patient
        response = self.client.post("/patient/register", data, follow=True)
        self.assertTemplateNotUsed(response, "/patient/registered")
        self.assertEqual(len(response.redirect_chain), 0)

    def test_registration_invalid_patient_form(self):
        self.client.login(username="test_name", password="test_pw")
        self.patient["patient-first_name"] = ""
        data = self.address | self.patient
        response = self.client.post("/patient/register", data, follow=True)
        self.assertTemplateNotUsed(response, "/patient/registered")
        self.assertEqual(len(response.redirect_chain), 0)


class TestSuccessRegistrationView(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_name",
            email="test@email.com",
            password="test_pw"
        )
        self.address = {
            "address-street": "Test Lane",
            "address-number": "12a",
            "address-apartment": "123",
            "address-zip_code": "00-000",
            "address-city": "Testington",
            "address-country": "Republic of Testland"
        }
        self.patient = {
            "patient-first_name": "Johnny",
            "patient-last_name": "Test",
            "patient-date_of_birth": "2022-12-12",
            "patient-personal_id": "12345678911",
            "patient-email": "email@email.com",
            "patient-phone": "0123456789"
        }

    def test_redirect_if_no_form_submitted(self):
        self.client.login(username="test_name", password="test_pw")
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
        self.address = Address.objects.create(
            street="Test Lane",
            number="12a",
            apartment="123",
            zip_code="00-000",
            city="Testington",
            country="Republic of Testland"
        )
        self.patient = Patient.objects.create(
            first_name="Johnny",
            last_name="Test",
            date_of_birth="2022-12-12",
            personal_id="12345678911",
            email="email@email.com",
            phone="0123456789",
            address=self.address
        )
        self.data = {
            "patient-first_name": "Johnny",
            "patient-last_name": "Test",
            "patient-date_of_birth": "2022-12-12",
            "patient-personal_id": "12345678911",
            "patient-email": "email@email.com",
            "patient-phone": "0123456789",
            "address-street": "Test Lane",
            "address-number": "12a",
            "address-apartment": "123",
            "address-zip_code": "00-000",
            "address-city": "Testington",
            "address-country": "Republic of Testland"
        }

    def test_get_redirects_anonymous_user_to_login(self):
        response = self.client.get("/patient/1", follow=True)
        self.assertRedirects(response, "/account/login?next=/patient/1")

    def test_post_redirects_anonymous_user_to_login(self):
        response = self.client.post("/patient/1", data=self.data, follow=True)
        self.assertRedirects(response, "/account/login?next=/patient/1")

    def test_patient_view_get_valid_patient_id(self):
        self.client.login(username="test_name", password="test_pw")
        response = self.client.get("/patient/1")
        self.assertTemplateUsed(response, "patients/patient.html")

    def test_patient_view_get_invalid_patient_id(self):
        self.client.login(username="test_name", password="test_pw")
        response = self.client.get("/patient/2")
        self.assertTemplateUsed(response, "404.html")

    def test_patient_view_post_data_changed(self):
        self.client.login(username="test_name", password="test_pw")
        self.data["patient-first_name"] = "James"
        self.data["address-city"] = "Test Peaks"
        response = self.client.post("/patient/1", data=self.data)
        self.assertRedirects(response, "/patient/1")

    def test_patient_view_post_data_not_changed(self):
        self.client.login(username="test_name", password="test_pw")
        response = self.client.post("/patient/1", data=self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.redirect_chain), 0)


class TestSearchResultsView(TestCase):

    def setUp(self):
        self.address = Address.objects.create(
            street="Test Lane",
            number="12a",
            apartment="123",
            zip_code="00-000",
            city="Testington",
            country="Republic of Testland"
        )
        self.patient_1 = Patient.objects.create(
            first_name="Johnny",
            last_name="Test",
            date_of_birth="2022-12-12",
            personal_id="12345678911",
            email="email@email.com",
            phone="0123456789",
            address=self.address
        )

    def test_search_result_view(self):
        response = self.client.get("/patient/search-results?query=test")
        self.assertTemplateUsed(response, "patients/search_results.html")

    def test_no_search_data_raises_404(self):
        response = self.client.get("/patient/search-results")
        self.assertTemplateUsed(response, "404.html")
