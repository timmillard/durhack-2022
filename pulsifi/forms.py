"""
    Forms in pulsifi app.
"""

from allauth.account.forms import SignupForm as Base_SignupForm
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm as Base_AuthenticationForm

from pulsifi.models import Pulse, Reply


class Login_Form(Base_AuthenticationForm):
    """ Form to customise the HTML & CSS generated for the login form. """

    template_name = "pulsifi/auth_form_snippet.html"
    """
        Link to a HTML snippet, which describes how the form should be rendered
        (see https://docs.djangoproject.com/en/4.1/topics/forms/#reusable-form-templates).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].label = "Username / Email Address"
        self.fields["username"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Enter your Username / Email Address"
            }
        )

        self.fields["password"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Enter your Password"
            }
        )

        self.label_suffix = ""


class Signup_Form(Base_SignupForm):
    """ Form to customise the HTML & CSS generated for the signup form. """

    template_name = "pulsifi/auth_form_snippet.html"
    """
        Link to a HTML snippet, which describes how the form should be rendered
        (see https://docs.djangoproject.com/en/4.1/topics/forms/#reusable-form-templates).
    """

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


class Pulse_Form(forms.ModelForm):
    """ Form for creating a new Pulse """

    class Meta:
        model = Pulse
        fields = ("creator", "message")  # TODO: creator should be automatically assigned (not be a selectable field)


class Reply_Form(forms.ModelForm):
    """ Form for creating a new reply. """

    class Meta:
        model = Reply
        fields = ("creator", "message")  # TODO: creator should be automatically assigned (not be a selectable field), add parent object field


class Bio_Form(forms.ModelForm):
    """ Form for updating a user's bio. """

    class Meta:
        model = get_user_model()
        fields = ("bio",)
