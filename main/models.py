from django.contrib.auth.models import User
from django.db import models

from patients.models import Patient


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
        default="DOCTOR REMOVED"
    )
    purpose = models.CharField(max_length=200, null=False)
    examination = models.TextField(null=True)
    diagnosis = models.CharField(max_length=250, null=True)
    advice = models.TextField(null=True)
    prescription = models.TextField(null=True)
    took_place = models.BooleanField(default=False)

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
