from django.db import models
from django.contrib.auth.models import User


class Schedule(models.Model):
    """
    Employee shift date, start time and end time.
    """

    date = models.DateField()
    start = models.TimeField()
    end = models.TimeField()
    employee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.emp_full_name()} {self.date}"

    def emp_full_name(self):
        return f"{self.employee.first_name} {self.employee.last_name}"
