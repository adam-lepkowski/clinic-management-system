from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from patients.models import Patient
from .validators import is_physician


class Schedule(models.Model):
    """
    Employee shift date, start time and end time.
    """

    date = models.DateField()
    start = models.TimeField()
    end = models.TimeField()
    employee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("date", "employee"),
                name="unique_employee_work_date",
                violation_error_message="Employee already has a shift"\
                    "scheduled for that day!"
            )
        ]

    def __str__(self):
        return f"{self.emp_full_name()} {self.date}"

    def emp_full_name(self):
        return f"{self.employee.first_name} {self.employee.last_name}"


class Appointment(models.Model):
    """
    Doctor appointments.
    """

    datetime = models.DateTimeField()
    patient = models.ForeignKey(
        Patient,
        on_delete=models.SET_DEFAULT,
        default="PATIENT REMOVED"
    )
    doctor = models.ForeignKey(
        User,
        on_delete=models.SET_DEFAULT,
        default="DOCTOR REMOVED",
        validators=[is_physician]
    )
    purpose = models.CharField(max_length=200, null=False)
    examination = models.TextField(null=True)
    diagnosis = models.CharField(max_length=250, null=True)
    advice = models.TextField(null=True)
    prescription = models.TextField(null=True)
    took_place = models.BooleanField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("datetime", "doctor"),
                name="unique_doctor_appointment",
                violation_error_message="Doctor already has an appointment at"\
                    "this datetime!"
            ),
            models.UniqueConstraint(
                fields=("datetime", "patient"),
                name="unique_patient_appointment",
                violation_error_message="Patient already has an appointment "\
                    "at this datetime!"
            )
        ]

    def clean(self):
        """
        Check if user in doctor field is a physician on schedule.
        """
        employee = User.objects.filter(
            models.Q(groups__name__iexact="physicians"),
            id=self.doctor.id
        )
        schedule = Schedule.objects.filter(
            models.Q(date=self.datetime),
            employee__id=self.doctor.id
        )

        if not employee.exists():
            raise ValidationError("User is not a physician!")
        elif not schedule.exists():
            raise ValidationError("Doctor not on schedule!")

    def __str__(self):
        datetime_string = self.datetime.strftime("%Y-%m-%d %H:%M")
        return f"{datetime_string} {self.doctor} {self.patient}"

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("main:appointment", args=[self.id])
