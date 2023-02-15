from django.test import TestCase

from ..models import Patient, Address


class TestRegistrationView(TestCase):

    def setUp(self):
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

    def test_registration_valid_forms(self):
        data = self.address | self.patient
        response = self.client.post("/patient/register", data, follow=True)
        self.assertRedirects(response, "/patient/registered")

    def test_registration_valid_forms_sets_session_attr(self):
        data = self.address | self.patient
        self.client.post("/patient/register", data)
        result = self.client.session.get("patient-registered", False)
        self.assertTrue(result)

    def test_registration_invalid_address_form(self):
        self.address["address-city"] = ""
        data = self.address | self.patient
        response = self.client.post("/patient/register", data, follow=True)
        self.assertTemplateNotUsed(response, "/patient/registered")
        self.assertEqual(len(response.redirect_chain), 0)

    def test_registration_invalid_patient_form(self):
        self.patient["patient-first_name"] = ""
        data = self.address | self.patient
        response = self.client.post("/patient/register", data, follow=True)
        self.assertTemplateNotUsed(response, "/patient/registered")
        self.assertEqual(len(response.redirect_chain), 0)


class TestSuccessRegistrationView(TestCase):

    def setUp(self):
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
        response = self.client.get("/patient/registered", follow=True)
        self.assertFalse(self.client.session.get("patient-registered", False))
        self.assertRedirects(response, "/patient/register")


class TestPatientView(TestCase):

    def setUp(self):
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

    def test_patient_view_get_valid_patient_id(self):
        response = self.client.get("/patient/1")
        self.assertTemplateUsed(response, "patients/patient.html")

    def test_patient_view_get_invalid_patient_id(self):
        response = self.client.get("/patient/2")
        self.assertTemplateUsed(response, "404.html")

    def test_patient_view_post_data_changed(self):
        self.data["patient-first_name"] = "James"
        self.data["address-city"] = "Test Peaks"
        response = self.client.post("/patient/1", data=self.data)
        self.assertRedirects(response, "/patient/1")
    
    def test_patient_view_post_data_not_changed(self):
        response = self.client.post("/patient/1", data=self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.redirect_chain), 0)