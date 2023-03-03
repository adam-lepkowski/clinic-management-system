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

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("date", "employee"),
                name="unique_employee_work_date",
                violation_error_message="Employee already has a shift"\
                    "scheduled for that day!")]

    def __str__(self):
        return f"{self.emp_full_name()} {self.date}"

    def emp_full_name(self):
        return f"{self.employee.first_name} {self.employee.last_name}"
