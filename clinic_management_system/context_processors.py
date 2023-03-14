import os

from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())


def get_kit(request):
    """
    Include fontawesome kit js to context.
    """

    data = {}
    data["kit"] = os.environ["FAWESOME_KIT"]
    return data


def get_user_group(request):
    """
    Check if logged belongs to nurses and physicians group.

    Returns
    ----------
    dict
        contains bool values for membership in nurses and physicians groups
    """

    user = request.user
    is_nurse = user.groups.filter(name__iexact="nurses").exists()
    is_doctor = user.groups.filter(name__iexact="physicians").exists()
    data = {
        "is_nurse": is_nurse,
        "is_doctor": is_doctor
    }
    return data
