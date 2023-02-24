from django import forms

from .models import Schedule


class ScheduleModelForm(forms.ModelForm):
    """
    Add an optional date_to field to Schedule model.

    Apply work time to a range of dates when upading schedule from admin page.
    """

    date_to = forms.DateField(label="Date to", required=False)

    class Meta:
        model = Schedule
        fields = ("date", "date_to", "start", "end", "employee")