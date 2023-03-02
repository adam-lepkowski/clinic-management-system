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

