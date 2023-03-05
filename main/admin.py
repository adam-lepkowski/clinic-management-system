from datetime import timedelta

from django.contrib import admin

from .models import Schedule
from .forms import ScheduleModelForm


class ScheduleAdmin(admin.ModelAdmin):
    """
    Display and manipulate Schedule model from admin page.
    """

    list_display = ("date", "start", "end", "employee")

    def get_form(self, request, obj=None, **kwargs):
        """
        Use custom ScheduleModelForm with extra date_to DateField.
        """

        kwargs["form"] = ScheduleModelForm
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        """
        Save multiple objects if a date range was selected. One otherwise.
        """

        date_from = form.cleaned_data["date"]
        date_to = form.cleaned_data["date_to"]

        if date_to and (date_from < date_to):
            delta = date_to - date_from
            for _ in range(delta.days + 1):
                super().save_model(request, obj, form, change)
                date_from += timedelta(days=1)
                obj.id += 1
                obj.date = date_from
        else:
            super().save_model(request, obj, form, change)


admin.site.register(Schedule, ScheduleAdmin)
