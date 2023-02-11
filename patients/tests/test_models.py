from django.test import TestCase

from ..models import Patient, Address


class TestPatient(TestCase):

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

    def test_patient_name(self):
        expected = "Johnny Test"
        self.assertEqual(expected, self.patient.name())

    def test_patient_str(self):
        expected = "Johnny Test"
        self.assertEqual(expected, str(self.patient))


class TestAddress(TestCase):

    def setUp(self):
        self.address = Address.objects.create(
            street="Test Lane",
            number="12a",
            apartment=None,
            zip_code="00-000",
            city="Testington",
            country="Republic of Testland"
        )


    def test_address_address_no_apartment(self):
        expected = "Test Lane 12a 00-000 Testington Republic of Testland"
        self.assertEqual(expected, self.address.address())
    
    def test_address_address_with_apartment(self):
        self.address.apartment = "12"
        self.address.save()
        expected = "Test Lane 12a/12 00-000 Testington Republic of Testland"
        self.assertEqual(expected, self.address.address())

    def test_address_str(self):
        expected = "Test Lane 12a 00-000 Testington Republic of Testland"
        self.assertEqual(expected, str(self.address))