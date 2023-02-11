from django.shortcuts import render
from django.views import View

from .forms import PatientForm, AddressForm


class RegistrationView(View):
    """
    Display patient registration form.
    """

    def get(self, request):
        """
        Display empty patient registration form.
        """

        patient_form = PatientForm(prefix="patient")
        address_form = AddressForm(prefix="address")
        context = {
            "patient_form": patient_form,
            "address_form": address_form
        }
        return render(request, "patients/register.html", context)