from django.urls import path
import django.contrib.auth.views as auth_views

from .views import ProfileView


app_name = "accounts"

urlpatterns = [
    path("login", auth_views.LoginView.as_view(
        template_name="accounts/login.html",
        redirect_authenticated_user=True)),
    path("logout", auth_views.LogoutView.as_view(), name="logout"),
    path("", ProfileView.as_view(), name="profile")
]
