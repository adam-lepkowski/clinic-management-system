from django.test import TestCase
from django.contrib.auth.models import User

from ..models import Schedule
from ..forms import ScheduleSearchForm


class TestScheduleSearchView(TestCase):

    def test_get(self):
        response = self.client.get("/schedule/search")
        self.assertIsInstance(response.context["form"], ScheduleSearchForm)
        self.assertTemplateUsed(response, "main/schedule.html")

    def test_ajax_get(self):
        response = self.client.get(
            "/schedule/search", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertTemplateUsed(response, "main/includes/specialists.html")
