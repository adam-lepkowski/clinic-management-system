from datetime import date, timedelta

from django import forms
from django.contrib.auth.models import Group

from .models import Schedule


AVAILABLE_DATES = [(i + 1, date.today() + timedelta(days=i)) for i in range(7)]


class ScheduleModelForm(forms.ModelForm):
    """
    Add an optional date_to field to Schedule model.

    Apply work time to a range of dates when upading schedule from admin page.
    """

    date_to = forms.DateField(
        label="Date to",
        required=False,
        widget=forms.SelectDateWidget)

    class Meta:
        model = Schedule
        fields = ("date", "date_to", "start", "end", "employee")


class ScheduleSearchForm(forms.Form):
    """
    Display doctors available for appointments.
    """

    specialties = forms.ModelChoiceField(queryset=Group.objects.all())
    date = forms.DateField(widget=forms.Select(choices=AVAILABLE_DATES))
