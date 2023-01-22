from django.shortcuts import render
from django.views import View


class MainView(View):
    """
    Display main page.
    """

    def get(self, request):
        """
        Render main page.
        """
        
        return render(request, "main/index.html")
