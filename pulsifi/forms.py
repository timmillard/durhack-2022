"""
    Forms in pulsifi application.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.contrib.auth.models import User


class UserCreationForm(BaseUserCreationForm):
    email = forms.EmailField(required=True)
    name = forms.CharField(max_length=30)

    class Meta:
        model = User
        fields = (
            "name",
            "email",
            "username",
            "password1",
            "password2",
        )