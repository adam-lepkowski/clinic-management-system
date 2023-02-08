from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin


class MainView(LoginRequiredMixin, View):
    """
    Display main page.
    """
    
    def get(self, request):
        """
        Render main page.
        """
        
        return render(request, "main/index.html")
