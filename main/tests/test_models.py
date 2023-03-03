from datetime import date

from django.test import TestCase
from django.contrib.auth.models import User
from django.db.utils import IntegrityError

from ..models import Schedule


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
                employee=self.user)
