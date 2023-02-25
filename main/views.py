from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

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
        Render empty schedule form.
        """
        
        form = ScheduleSearchForm()
        context = {
            "form": form
        }

        return render(request, "main/schedule.html", context)