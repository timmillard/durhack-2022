"""
    Forms in pulsifi app.
"""

from allauth.account.forms import SignupForm as BaseSignupForm
from django import forms

from pulsifi.models import Profile, Pulse, Reply


class SignupForm(BaseSignupForm):
    """ Form to customise the HTML & CSS generated for the signup form. """

    template_name = "pulsifi/signup_form_snippet.html"  # Specify how the fields & labels of the form should be turned into HTML

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

        self.label_suffix = ""  # Remove the colon from after the value, in the field label


class PulseForm(forms.ModelForm):
    """ Form for creating a new Pulse """

    class Meta:
        model = Pulse
        fields = ("creator", "message")  # TODO: creator should be automatically assigned (not be a selectable field)


class ReplyForm(forms.ModelForm):
    """ Form for creating a new reply. """

    class Meta:
        model = Reply
        fields = ("creator", "message")  # TODO: creator should be automatically assigned (not be a selectable field), add parent object field


class BioForm(forms.ModelForm):
    """ Form for updating a user's bio. """

    class Meta:
        model = Profile
        fields = ("bio",)
