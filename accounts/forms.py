from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class ProfileForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].disabled = True
        self.fields["first_name"].disabled = True
        self.fields["last_name"].disabled = True
        self.fields["email"].disabled = True

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]