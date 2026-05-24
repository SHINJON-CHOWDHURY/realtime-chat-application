from django import forms

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import UserProfile


# =========================
# REGISTER FORM
# =========================
class RegisterForm(UserCreationForm):

    email = forms.EmailField(
        required=True
    )

    class Meta:

        model = User

        fields = [
            "username",
            "email",
            "password1",
            "password2"
        ]


# =========================
# EDIT PROFILE FORM
# =========================
class EditProfileForm(forms.ModelForm):

    username = forms.CharField(
        max_length=150
    )

    class Meta:

        model = UserProfile

        fields = [
            "profile_picture"
        ]

    def __init__(
        self,
        *args,
        **kwargs
    ):

        user = kwargs.pop(
            "user",
            None
        )

        super().__init__(
            *args,
            **kwargs
        )

        if user:

            self.fields[
                "username"
            ].initial = user.username