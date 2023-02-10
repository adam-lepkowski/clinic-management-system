from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm


class ProfileForm(forms.ModelForm):
    """
    Represent uneditable user profile data.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].disabled = True
        self.fields["first_name"].disabled = True
        self.fields["last_name"].disabled = True
        self.fields["email"].disabled = True

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]


class PwdChangeForm(PasswordChangeForm):
    """
    Change currently logged in user password.
    """
        
    new_password2 = forms.CharField(
        label=("Confirm new password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""