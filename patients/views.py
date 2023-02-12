from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
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
                request.session["patient-registered"] = True
                return HttpResponseRedirect(reverse("patients:registered"))

        context = {
            "patient_form": patient_form,
            "address_form": address_form
        }
        return render(request, "patients/register.html", context)


class SuccessRegistrationView(View):
    """
    Redirect page after successful patient registration.
    """
    
    def get(self, request):
        """
        Display success page if redirected after successful patient
        registration. Redirect to registration form otherwise.
        """

        if request.session.get("patient-registered", False):
            request.session["patient-registered"] = False
            return render(request, "patients/success_register.html")
        
        return HttpResponseRedirect(reverse("patients:register"))