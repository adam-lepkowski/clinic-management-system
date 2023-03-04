import datetime

from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render
from django.views import View

from .forms import ScheduleSearchForm
from .models import Schedule
from .utils import get_day_schedule


class MainView(LoginRequiredMixin, View):
    """
    Display main page.
    """

    def get(self, request):
        """
        Render main page.
        """

        return render(request, "main/index.html")


class ScheduleSearchView(LoginRequiredMixin, View):
    """
    Display schedule search form
    """

    def get(self, request):
        """
        Schedule form page or selected specialists for ajax request.
        """

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            specialty = request.GET.get("specialty")
            specialists = User.objects.filter(groups__name=specialty)
            context = {"specialists": specialists}
            return render(request, "main/includes/specialists.html", context)

        form = ScheduleSearchForm()
        context = {
            "form": form
        }

        return render(request, "main/schedule.html", context)


class ScheduleListView(View):
    """
    Display schedule search results.
    """

    def get(self, request):
        """
        Search results.
        """

        spec_id = request.GET.get("specialties")
        emp_id = request.GET.get("employee", None)
        date = request.GET.get("date")
        if emp_id:
            schedules = Schedule.objects.filter(Q(employee__groups__id=spec_id)
                                                & Q(employee__id=emp_id)
                                                & Q(date=date))
        else:
            schedules = Schedule.objects.filter(Q(employee__groups__id=spec_id)
                                                & Q(date=date))

        context = {
            "date": datetime.datetime.strptime(date, "%Y-%m-%d"),
            "schedule": get_day_schedule(schedules)
        }
        return render(request, "main/schedule_search_results.html", context)
