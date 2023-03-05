from datetime import date

from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils import timezone

from patients.models import Patient
from ..models import Schedule, Appointment


class TestSchedule(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username="TestUser",
            first_name="Teston",
            last_name="Testingly"
        )
        self.schedule = Schedule.objects.create(
            date="2023-01-01",
            start="08:00",
            end="16:00",
            employee=self.user
        )

    def test_remove_user_sets_schedule_null(self):
        self.user.delete()
        schedule = Schedule.objects.get(id=1)
        self.assertEqual(schedule.employee, None)
        self.assertEqual(schedule.date, date(2023, 1, 1))

    def test_cant_schedule_the_same_day_twice_single_employee(self):
        with self.assertRaises(IntegrityError):
            Schedule.objects.create(
                date="2023-01-01",
                start="08:00",
                end="16:00",
                employee=self.user
            )


class TestAppointment(TestCase):

    def setUp(self):
        self.physicians_group = Group.objects.create(
            name="physicians"
        )
        self.patient = Patient.objects.create(
            first_name="Johnny",
            last_name="Test",
            date_of_birth="2022-12-12",
            personal_id="12345678911",
            email="email@email.com",
            phone="0123456789",
            address=None
        )

    def test_appointment_with_not_a_doctor_not_possible(self):
        not_doctor = User.objects.create_user(
            username="TestUserNotADoctor",
            first_name="NotDoctor",
            last_name="NotDoctorly"
        )
        Schedule.objects.create(
            date=timezone.now(),
            start="08:00",
            end="16:00",
            employee=not_doctor
        )
        with self.assertRaises(ValidationError):
            Appointment.objects.create(
                datetime=timezone.now(),
                patient=self.patient,
                doctor=not_doctor,
                purpose="Toothache",
                examination=None,
                diagnosis=None,
                advice=None,
                prescription=None,
                took_place=False
            )

    def test_appointment_with__doctor_not_on_schedule_not_possible(self):
        doctor = User.objects.create_user(
            username="TestUserNotADoctor",
            first_name="NotDoctor",
            last_name="NotDoctorly"
        )
        doctor.groups.add(self.physicians_group)
        with self.assertRaises(ValidationError):
            Appointment.objects.create(
                datetime=timezone.now(),
                patient=self.patient,
                doctor=doctor,
                purpose="Toothache",
                examination=None,
                diagnosis=None,
                advice=None,
                prescription=None,
                took_place=False
            )
