from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.base import TemplateView

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

    def post(self, request):
        """
        Save registered patient details or display page with error messages.
        """

        patient_form = PatientForm(request.POST, prefix="patient")
        address_form = AddressForm(request.POST, prefix="address")

        if address_form.is_valid():
            if patient_form.is_valid():
                address = address_form.save()
                patient = patient_form.save(commit=False)
                patient.address = address
                patient.save()
                return redirect("/patient/registered")

        context = {
            "patient_form": patient_form,
            "address_form": address_form
        }
        return render(request, "patients/register.html", context)


class SuccessRegistrationView(TemplateView):
    template_name = "patients/success_register.html"