from datetime import datetime, timedelta

from django.test import TestCase
from django.contrib.auth.models import User

from ..models import Schedule
from ..utils import get_day_schedule
from ..const import APPOINTMENT_TIME


class TestGetDaySchedule(TestCase):

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
    
    def test_get_day_schedule(self):
        result = get_day_schedule(Schedule.objects.get(id=1))
        start = datetime(2022, 10, 10, hour=8)
        expected = [start + timedelta(minutes=APPOINTMENT_TIME * i) for i in range(16)]
        expected = [dt.time() for dt in expected]
        self.assertEqual(expected, result)