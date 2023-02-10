from django.urls import path
import django.contrib.auth.views as auth_views

from .views import ProfileView
from .forms import PwdChangeForm


app_name = "accounts"

urlpatterns = [
    path("login", auth_views.LoginView.as_view(
        template_name="accounts/login.html",
        redirect_authenticated_user=True)),
    path("logout", auth_views.LogoutView.as_view(), name="logout"),
    path("", ProfileView.as_view(), name="profile"),
    path("change-password", auth_views.PasswordChangeView.as_view(
            template_name="accounts/change_password.html",
            form_class=PwdChangeForm,
            success_url="password-changed")),
    path("password-changed", auth_views.PasswordChangeDoneView.as_view(
            template_name="accounts/password_changed.html"
    ), name="password_change_done")
]
