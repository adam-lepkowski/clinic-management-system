from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic import ListView

from .forms import PatientForm, AddressForm
from .models import Patient


class RegistrationView(LoginRequiredMixin, View):
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
            "address_form": address_form,
            "mode": "Register"
        }
        return render(request, "patients/register.html", context)

    def post(self, request):
        """
        Save registered patient details or display page with error messages.
        """

        patient_form = PatientForm(request.POST, prefix="patient")
        address_form = AddressForm(request.POST, prefix="address")

        if address_form.is_valid() and patient_form.is_valid():
            address = address_form.save()
            patient = patient_form.save(commit=False)
            patient.address = address
            patient.save()
            request.session["patient-registered"] = True
            return HttpResponseRedirect(reverse("patients:registered"))

        context = {
            "patient_form": patient_form,
            "address_form": address_form,
            "mode": "Register"
        }
        return render(request, "patients/register.html", context)


class SuccessRegistrationView(LoginRequiredMixin, View):
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


class PatientView(LoginRequiredMixin, View):
    """
    Display single patient personal information and treatment history.
    """

    def get(self, request, pk):
        """
        Display single patient details in a editable form.
        """

        patient = get_object_or_404(Patient, id=pk)
        patient_form = PatientForm(instance=patient, prefix="patient")
        address_form = AddressForm(instance=patient.address, prefix="address")
        context = {
            "patient_form": patient_form,
            "address_form": address_form,
            "mode": "Update"
        }
        return render(request, "patients/patient.html", context)

    def post(self, request, pk):
        """
        Update patient personal details and display them imidiately on success.
        Display page with errors otherwise.
        """

        patient = get_object_or_404(Patient, id=pk)
        patient_form = PatientForm(
            request.POST, instance=patient, prefix="patient"
        )
        address_form = AddressForm(
            request.POST, instance=patient.address, prefix="address"
        )

        if ((patient_form.changed_data or address_form.changed_data)
                and (address_form.is_valid() and patient_form.is_valid())):
            address_form.save()
            patient_form.save()
            return HttpResponseRedirect(reverse("patients:patient", args=[pk]))

        context = {
            "patient_form": patient_form,
            "address_form": address_form,
            "mode": "Update"
        }
        return render(request, "patients/patient.html", context)


class SearchResultsView(LoginRequiredMixin, ListView):
    """
    Display patient search results.
    """

    model = Patient
    template_name = "patients/search_results.html"
    context_object_name = "patients"

    def get_queryset(self):
        """
        Check for searched phrase in first_name, last_name and personal_id
        """

        base = super().get_queryset()
        q = self.request.GET.get("query", None)
        if q:
            data = base.filter(
                Q(first_name__icontains=q)
                | Q(last_name__icontains=q)
                | Q(personal_id__icontains=q)
            )
            return data
        raise Http404()
