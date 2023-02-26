"""
    Forms in pulsifi app.
"""
import logging

from allauth.account.forms import LoginForm as Base_LoginForm, SignupForm as Base_SignupForm
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from pulsifi.models import Pulse, Reply


class Login_Form(Base_LoginForm):
    """ Form to customise the HTML & CSS generated for the login form. """

    template_name = "pulsifi/auth_form_snippet.html"
    """
        Link to a HTML snippet, which describes how the form should be rendered
        (see https://docs.djangoproject.com/en/4.1/topics/forms/#reusable-form-templates).
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields["login"].label = "Username / Email Address"
        self.fields["login"].widget.attrs.update(
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

    def __init__(self, *args, **kwargs) -> None:
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

    def clean(self) -> dict[str]:
        """ Validate inserted form data using temporary in-memory user object. """

        super().clean()

        # if "username" in self.cleaned_data and "password1" in self.cleaned_data and "email" in self.cleaned_data:
        try:
            get_user_model()(  # TODO: perform model clean with out all input values
                username=self.cleaned_data.get("username") or "???",
                password=self.cleaned_data.get("password1") or "???",
                email=self.cleaned_data.get("email") or "???"
            ).full_clean()
        except ValidationError as e:
            self.add_errors_from_ValidationError_exception(e)

        return self.cleaned_data

    def add_errors_from_ValidationError_exception(self, exception: ValidationError, model_field_name: str = None) -> None:
        """
            Adds the error message(s) from any caught ValidationError exceptions
            to the forms errors dictionary/list.
        """

        if not hasattr(exception, "error_dict") and hasattr(exception, "error_list"):
            for error in exception.error_list:
                if model_field_name:
                    self.add_error(model_field_name, error)
                else:
                    self.add_error(None, error)
        elif hasattr(exception, "error_dict"):
            for field_name, errors in exception.error_dict.items():
                if field_name == "__all__":
                    self.add_error(None, errors)
                else:
                    self.add_error(field_name, errors)
        else:
            logging.error(f"Validation error {repr(exception)} raised without a field name supplied.")
        logging.debug([self.errors])


class Pulse_Form(forms.ModelForm):
    """ Form for creating a new Pulse """

    # noinspection PyMissingOrEmptyDocstring
    class Meta:
        model = Pulse
        fields = ("creator", "message")  # TODO: creator should be automatically assigned (not be a selectable field)


class Reply_Form(forms.ModelForm):
    """ Form for creating a new reply. """

    # noinspection PyMissingOrEmptyDocstring
    class Meta:
        model = Reply
        fields = ("creator", "message")  # TODO: creator should be automatically assigned (not be a selectable field), add parent object field


class Bio_Form(forms.ModelForm):
    """ Form for updating a user's bio. """

    # noinspection PyMissingOrEmptyDocstring
    class Meta:
        model = get_user_model()
        fields = ("bio",)
