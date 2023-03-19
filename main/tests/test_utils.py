from datetime import datetime, time, date
from unittest.mock import patch, Mock, MagicMock

from django.test import TestCase

from ..utils import (get_appointment_times, get_day_schedule,
                     get_next_appointment, is_appointment_available)


class TestGetAppointmentTimes(TestCase):

    @patch("main.utils.datetime")
    def test_get_appointment_times(self, mock_datetime):
        side_effect = [datetime(2023, 1, 1, 8), datetime(2023, 1, 1, 9)]
        mock_datetime.combine.side_effect = side_effect
        mock_schedule = Mock()
        result = get_appointment_times(mock_schedule)
        expected = [time(8), time(8, 30)]
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

    def setUp(self):
        self.comparison_magic_mock = MagicMock()
        self.comparison_magic_mock.__lt__.return_value = False

    @patch("main.utils.datetime")
    @patch("main.utils.Appointment.objects")
    def test_appointment_available(self, mock_appointment, mock_datetime):
        mock_datetime.now.return_value = self.comparison_magic_mock
        mock_datetime.combine.return_value = self.comparison_magic_mock
        mock_appointment.filter.return_value = False
        result = is_appointment_available("1", date(2023, 1, 1), time(8, 30))
        self.assertTrue(result)

    @patch("main.utils.datetime")
    @patch("main.utils.Appointment.objects")
    def test_appointment_not_available(self, mock_appointment, mock_datetime):
        mock_datetime.now.return_value = self.comparison_magic_mock
        mock_datetime.combine.return_value = self.comparison_magic_mock
        mock_appointment.filter.return_value = True
        result = is_appointment_available("1", date(2023, 1, 1), time(8, 30))
        self.assertFalse(result)

    @patch("main.utils.datetime")
    @patch("main.utils.Appointment.objects")
    def test_appointment_datetime_less_than_now(
            self, mock_appointment, mock_datetime):
        self.comparison_magic_mock.__lt__.return_value = True
        mock_datetime.now.return_value = self.comparison_magic_mock
        mock_datetime.combine.return_value = self.comparison_magic_mock
        result = is_appointment_available("1", date(2023, 1, 1), time(8, 30))
        self.assertFalse(result)
