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