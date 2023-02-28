from django.shortcuts import render
from django.views import View
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q

from .forms import ScheduleSearchForm
from .models import Schedule


class MainView(LoginRequiredMixin, View):
    """
    Display main page.
    """

    def get(self, request):
        """
        Render main page.
        """

        return render(request, "main/index.html")


class ScheduleSearchView(View):
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
        emp_id = request.GET.get("employee")
        date = request.GET.get("date")
        data = Schedule.objects.filter(Q(employee__groups__id=spec_id)
                                       & Q(employee__id=emp_id)
                                       & Q(date=date))
        context = {
            "dates": data
        }
        return render(request, "main/schedule_search_results.html", context)
