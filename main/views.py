from django.shortcuts import render
from django.views import View


class MainView(View):
    """
    Display main page.
    """

    def get(self, request):
        return render(request, "main/index.html")
