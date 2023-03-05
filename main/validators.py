from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


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