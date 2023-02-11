from django.test import TestCase


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
