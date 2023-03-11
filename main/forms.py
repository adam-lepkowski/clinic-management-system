from datetime import date, timedelta

from django import forms
from django.contrib.auth.models import Group, User

from .models import Schedule, Appointment


AVAILABLE_DATES = [date.today() + timedelta(days=i) for i in range(7)]
AVAILABLE_DATES = [(d, d) for d in AVAILABLE_DATES]


class ScheduleModelForm(forms.ModelForm):
    """
    Add an optional date_to field to Schedule model.

    Apply work time to a range of dates when upading schedule from admin page.
    """

    date_to = forms.DateField(
        label="Date to",
        required=False,
        widget=forms.SelectDateWidget
    )

    class Meta:
        model = Schedule
        fields = ("date", "date_to", "start", "end", "employee")


class ScheduleSearchForm(forms.Form):
    """
    Display doctors available for appointments.
    """

    specialties = forms.ModelChoiceField(queryset=Group.objects.all())
    date = forms.DateField(widget=forms.Select(choices=AVAILABLE_DATES))
    employee = forms.ModelChoiceField(
        queryset=User.objects.none(), required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "employee" in self.data:
            try:
                emp_id = int(self.data.get("employee"))
                self.fields["employee"].queryset = User.objects.filter(
                    id=emp_id
                )
            except (ValueError, TypeError):
                pass


class AppointmentConfirmForm(forms.Form):
    """
    Get patient personal ID and visit purpose.
    """

    personal_id = forms.CharField(max_length=11)
    purpose = forms.CharField(max_length=200, widget=forms.Textarea)


class AppointmentModelForm(forms.ModelForm):
    """
    View scheduled appointment details.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["doctor"].disabled = True
        self.fields["patient"].disabled = True
        self.fields["datetime"].disabled = True
        self.fields["prescription"].required = False

    class Meta:
        model = Appointment
        fields = "__all__"
