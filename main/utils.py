from datetime import datetime, timedelta

from django.db.models import Q

from .const import APPOINTMENT_TIME
from .models import Appointment


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
        contains Schedule objects.

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
            if is_appointment_available(schedule.employee, schedule.date, hour):
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


def get_next_appointment(doctor):
    """
    Return doctors next appointment or None if there isn't one.

    Parameters
    ----------
    doctor : User
        user assigned to physicians group

    Returns
    ----------
    Appointment or None
        doctors next appointment or None if there isn't one
    """

    appointments = Appointment.objects.filter(
        Q(doctor=doctor)
        & Q(took_place=None)).order_by("datetime")
    if appointments:
        return appointments[0]
    return None


def is_appointment_available(doctor, date, hour):
    """
    Check if a doctor has no appointments scheduled at given datetime.

    Parameters
    ----------
    doctor : User
        user assigned to physicians group
    date : datetime.date
        appointment date
    hour : datetime.time
        appointment time

    Returns
    ----------
    bool
        True if datetime free to schedule, False otherwise.
    """

    appointment_datetime = datetime.combine(date, hour)

    if appointment_datetime < datetime.now():
        return False

    scheduled_appointment = Appointment.objects.filter(
        Q(doctor=doctor)
        & Q(datetime=appointment_datetime)
    )

    if scheduled_appointment:
        return False
    return True
