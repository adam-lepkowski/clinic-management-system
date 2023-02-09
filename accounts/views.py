from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import ProfileForm


class ProfileView(LoginRequiredMixin, View):
    """
    Display currently logged in user details.
    """

    def get(self, request):
        """
        Display currently logged in user details. 
        """

        context = {
            "form": ProfileForm(instance=request.user, label_suffix="")
        }
        return render(request, "accounts/profile.html", context)
