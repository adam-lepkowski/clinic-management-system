from django.urls import path

from .views import RegistrationView, SuccessRegistrationView, PatientView

app_name = "patients"

urlpatterns = [
    path("register", RegistrationView.as_view(), name="register"),
    path("registered", SuccessRegistrationView.as_view(), name="registered"),
    path("<int:pk>", PatientView.as_view(), name="patient")
]
