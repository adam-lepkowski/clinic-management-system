from datetime import datetime, timedelta, time, date
from unittest.mock import patch, Mock

from django.test import TestCase
from django.contrib.auth.models import User

from ..models import Schedule, Appointment
from ..utils import (get_appointment_times, get_day_schedule,
                     get_next_appointment, is_appointment_available)
from ..const import APPOINTMENT_TIME


class TestGetAppointmentTimes(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username="TestUser",
            first_name="Teston",
            last_name="Testingly"
        )
        Schedule.objects.create(
            date="2023-01-01",
            start="08:00",
            end="16:00",
            employee=self.user)

    def test_get_appointment_times(self):
        result = get_appointment_times(Schedule.objects.get(id=1))
        start = datetime(2022, 10, 10, hour=8)
        expected = [start + timedelta(minutes=APPOINTMENT_TIME * i)
                    for i in range(16)]
        expected = [dt.time() for dt in expected]
        self.assertEqual(expected, result)


class TestGetDaySchedule(TestCase):

    @patch("main.utils.is_appointment_available", return_value=True)
    @patch("main.utils._sort_day_schedule_by_hour", return_value=["10", "8", "9"])
    @patch("main.models.Schedule")
    @patch("main.utils.get_appointment_times", return_value=["8", "9", "10"])
    def test_get_day_schedule(
            self, mock_appointments, mock_schedule, mock_sort_hour,
            mock_is_appointment_available):
        mock_schedule.emp_full_name.return_value = "Teston Testingly"
        mock_schedule.employee.id = "1"
        mock_schedule.date = "2023-01-01"
        result = get_day_schedule([mock_schedule])
        expected = [
            {
                "employee_id": "1",
                "employee_full_name": "Teston Testingly",
                "date": "2023-01-01",
                "hour": "8",
            }, {
                "employee_id": "1",
                "employee_full_name": "Teston Testingly",
                "date": "2023-01-01",
                "hour": "9",
            }, {
                "employee_id": "1",
                "employee_full_name": "Teston Testingly",
                "date": "2023-01-01",
                "hour": "10",
            }
        ]
        self.assertEqual(expected, result)

    @patch("main.utils.is_appointment_available", return_value=False)
    @patch("main.models.Schedule")
    @patch("main.utils.get_appointment_times", return_value=["8", "9", "10"])
    def test_get_day_schedule_appointment_unavailable(
            self, mock_appointments, mock_schedule,
            mock_is_appointment_available):
        expected = []
        result = get_day_schedule([mock_schedule])
        self.assertEqual(expected, result)


class TestGetNextAppointment(TestCase):

    @patch("main.utils.Appointment.objects")
    def test_get_appointment_returns_appointment(self, mock_appointment):
        mock_appointment.filter.return_value = mock_appointment
        mock_appointment.order_by.return_value = [1, 2]
        expected = 1
        result = get_next_appointment("user")
        self.assertEqual(expected, result)

    def test_get_appointment_returns_none(self):
        result = get_next_appointment(1)
        self.assertIsNone(result)


class TestIsAppointmentAvailable(TestCase):

    @patch("main.utils.Appointment.objects")
    def test_appointment_available(self, mock_appointment):
        mock_appointment.filter.return_value = False
        result = is_appointment_available("1", date(2023, 1, 1), time(8, 30))
        self.assertTrue(result)

    @patch("main.utils.Appointment.objects")
    def test_appointment_not_available(self, mock_appointment):
        mock_appointment.filter.return_value = True
        result = is_appointment_available("1", date(2023, 1, 1), time(8, 30))
        self.assertFalse(result)
