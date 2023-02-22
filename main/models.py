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
