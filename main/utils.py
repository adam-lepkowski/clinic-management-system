from datetime import datetime, timedelta

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
    list
        dictionaries of appointment details.
    """

    day_schedule_by_available_hours = []
    for schedule in schedules:
        available_hours = get_appointment_times(schedule)
        for hour in available_hours:
            appointment_details = {
                "employee_id": schedule.employee.id,
                "employee_full_name": schedule.emp_full_name,
                "date": schedule.date,
                "hour": hour}
            day_schedule_by_available_hours.append(appointment_details)
    return day_schedule_by_available_hours
