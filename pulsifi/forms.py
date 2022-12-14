"""
    Forms in pulsifi application.
"""

from allauth.account.forms import SignupForm as BaseSignupForm
from django import forms

from pulsifi.models import Profile, Pulse, Reply


class SignupForm(BaseSignupForm):
    template_name = "pulsifi/signup_form_snippet.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["email"].label = "Email Address"
        self.fields["email"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Enter your Email Address"
            }
        )

        self.fields["username"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Choose a Username"
            }
        )

        self.fields["password1"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Choose a Password"
            }
        )

        self.fields["password2"].label = "Confirm Password"
        self.fields["password2"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Re-enter your Password, to check that you can spell"
            }
        )

        self.label_suffix = ""

    def save(self, request):
        base_user = super().save(request)
        Profile.objects.create(_base_user=base_user)
        return base_user


class PulseForm(forms.ModelForm):
    class Meta:
        model = Pulse
        fields = ("creator", "message")


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ("creator", "message")


class BioForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("bio",)