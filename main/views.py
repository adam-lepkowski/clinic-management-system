import datetime

from django.db.models import Q
from django.db.utils import IntegrityError
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from .forms import (
    ScheduleSearchForm, AppointmentConfirmForm, AppointmentModelForm
)
from .models import Schedule, Appointment
from .utils import get_day_schedule, get_next_appointment
from patients.models import Patient


class MainView(LoginRequiredMixin, View):
    """
    Display main page.
    """

    def get(self, request):
        """
        Render main page.
        """

        doctor = self.request.user
        appointment = get_next_appointment(doctor)
        if appointment:
            form = AppointmentModelForm(
                instance=appointment,
                label_suffix=""
            )
            context = {
                "form": form
            }
            return render(request, "main/index.html", context)
        return render(request, "main/index.html")


class ScheduleSearchView(LoginRequiredMixin, View):
    """
    Display schedule search form
    """

    def get(self, request):
        """
        Schedule form page or selected specialists for ajax request.
        """

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            specialty = request.GET.get("specialty")
            specialists = User.objects.filter(groups__name=specialty)
            context = {"specialists": specialists}
            return render(request, "main/includes/specialists.html", context)

        form = ScheduleSearchForm()
        context = {
            "form": form
        }

        return render(request, "main/schedule.html", context)


class ScheduleListView(LoginRequiredMixin, View):
    """
    Display schedule search results.
    """

    def get(self, request):
        """
        Get search results or redirect to schedule search form if ivalid values
        provided.
        """

        spec_id = request.GET.get("specialties")
        emp_id = request.GET.get("employee")
        date = request.GET.get("date")
        if spec_id is None or date is None:
            return HttpResponseRedirect(reverse("main:schedule"))
        elif emp_id:
            schedules = Schedule.objects.filter(
                Q(employee__groups__id=spec_id)
                & Q(employee__id=emp_id)
                & Q(date=date)
            )
        else:
            schedules = Schedule.objects.filter(
                Q(employee__groups__id=spec_id)
                & Q(date=date)
            )

        context = {
            "date": datetime.datetime.strptime(date, "%Y-%m-%d"),
            "schedule": get_day_schedule(schedules)
        }
        return render(request, "main/schedule_search_results.html", context)

    def post(self, request):
        """
        Store appointment details in session and redirect to confirmation page.
        """

        request.session["hour"] = request.POST.get("hour")
        request.session["date"] = request.POST.get("date")
        request.session["doctor_id"] = request.POST.get("doctor_id")

        return HttpResponseRedirect(reverse("main:confirm_appointment"))


class AppointmentConfirmView(LoginRequiredMixin, View):
    """
    Select a patient and confirm appointment.
    """

    def get(self, request):
        """
        Display confirmation form or redirect to schedule form if no valid
        session data found.
        """

        date_string = request.session.get("date")
        time_string = request.session.get("hour")
        doctor_id = request.session.get("doctor_id")
        if (date_string is None
                or time_string is None
                or doctor_id is None):
            return HttpResponseRedirect(reverse("main:schedule"))

        form = AppointmentConfirmForm(label_suffix="")
        context = {
            "form": form
        }
        return render(request, "main/appointment_confirm.html", context)

    def post(self, request):
        """
        Confirm appointment and redirect if valid. Display errors otherwise.
        """

        form = AppointmentConfirmForm(request.POST)
        context = {
            "form": form
        }

        if form.is_valid():
            personal_id = form.cleaned_data["personal_id"]
            try:
                patient = Patient.objects.get(personal_id=personal_id)
            except Patient.DoesNotExist as e:
                context["error"] = "Invalid patient id"
                return render(request, "main/appointment_confirm.html", context)

            date_string = request.session.get("date")
            time_string = request.session.get("hour")
            doctor_id = request.session.get("doctor_id")
            if (date_string is None
                    or time_string is None
                    or doctor_id is None):
                context["error"] = "Fill out schedule form first."
                return render(request, "main/appointment_confirm.html", context)

            try:
                doctor = User.objects.get(pk=doctor_id)
            except User.DoesNotExist as e:
                context["error"] = "Invalid doctor ID"
                return render(request, "main/appointment_confirm.html", context)

            date = datetime.datetime.strptime(date_string, "%Y-%m-%d").date()
            time = datetime.datetime.strptime(time_string, "%H:%M").time()
            appointment_datetime = datetime.datetime.combine(date, time)
            try:
                appointment = Appointment(
                    datetime=appointment_datetime,
                    patient=patient,
                    doctor=doctor,
                    purpose=form.cleaned_data["purpose"]
                )
                appointment.save()
            except IntegrityError as e:
                context["error"] = str(e)
                return render(request, "main/appointment_confirm.html", context)

            return HttpResponseRedirect(reverse("main:main"))

        else:
            return render(request, "main/appointment_confirm.html", context)
