from django.forms import ModelForm

from .models import Patient, Address


class PatientForm(ModelForm):
    """
    Represent Patient model fields.
    """

    class Meta:
        model = Patient
        fields = [
            "first_name",
            "last_name",
            "date_of_birth",
            "personal_id",
            "email",
            "phone"
        ]


class AddressForm(ModelForm):
    """
    Represent Address model fields.
    """

    class Meta:
        model = Address
        fields = [
            "street",
            "number",
            "apartment",
            "zip_code",
            "city",
            "country"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["apartment"].required = False
