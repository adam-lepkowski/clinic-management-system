from datetime import datetime, timedelta
from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth.models import User

from ..models import Schedule
from ..utils import get_appointment_times, get_day_schedule
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
    maxDiff = None

    @patch("main.models.Schedule")
    @patch("main.utils.get_appointment_times", return_value=["8", "9", "10"])
    def test_get_day_schedule(self, mock_appointments, mock_schedule):
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
