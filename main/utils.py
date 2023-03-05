from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .const import APPOINTMENT_TIME


def get_appointment_times(schedule):
    """
    Part workday into available appoitnments.

    Parameters
    ----------
    schedule : Schedule.

    Returns
    ----------
    list
        time objects representing available appointments.        
    """

    start_dt = datetime.combine(schedule.date, schedule.start)
    end_dt = datetime.combine(schedule.date, schedule.end)
    delta = timedelta(minutes=APPOINTMENT_TIME)
    available_hours = []

    while start_dt < end_dt:
        available_hours.append(start_dt.time())
        start_dt += delta

    return available_hours


def get_day_schedule(schedules):
    """
    Get all available employees working hours at a given day.

    Parameters
    ----------
    schedules : list
                Contains Schedule objects.

    Returns
    ----------
    list of dictionaries
        employee_id : int
        employee_full_name : str
        date : datetime.date
        hour : datetime.time
    """

    day_schedule_by_available_hours = []
    for schedule in schedules:
        available_hours = get_appointment_times(schedule)
        for hour in available_hours:
            appointment_details = {
                "employee_id": schedule.employee.id,
                "employee_full_name": schedule.emp_full_name(),
                "date": schedule.date,
                "hour": hour}
            day_schedule_by_available_hours.append(appointment_details)
    return sorted(day_schedule_by_available_hours, key=_sort_day_schedule_by_hour)


def _sort_day_schedule_by_hour(appointment):
    """
    Sort appointments ascending by hour.
    """

    return appointment["hour"].strftime("%H:%M")


def is_physician(user_id):
    """
    Raise ValidationError if user is not a physician.

    Parameters
    ----------
    user_id : int

    Raises
    ----------
    ValidationError
        If user is not assigned to group "physicians".
    """

    user = User.objects.get(pk=user_id)
    if not user.groups.filter(name__iexact="physicians").exists():
        raise ValidationError("User is not a physician!")
