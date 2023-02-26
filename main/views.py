from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User

from .forms import ScheduleSearchForm


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
