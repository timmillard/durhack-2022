"""
    Forms in pulsifi app.
"""

import logging

from allauth.account.forms import LoginForm as Base_LoginForm, SignupForm as Base_SignupForm
from django import forms
from django.contrib import auth
from django.core.exceptions import ValidationError

from pulsifi.models import Pulse, Reply

get_user_model = auth.get_user_model  # NOTE: Adding external package functions to the global scope for frequent usage


class _Base_Form_Config(forms.Form):
    """
        Config class to provide the base attributes for how to configure a
        form.
    """

    template_name = "pulsifi/base_form_snippet.html"
    """
        Link to a HTML snippet, which describes how the form should be rendered
        (see https://docs.djangoproject.com/en/4.1/topics/forms/#reusable-form-templates).
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        visible_field: forms.BoundField
        for visible_field in self.visible_fields():
            if visible_field.widget_type not in ("checkbox", "radio"):
                visible_field.field.widget.attrs["class"] = "form-control"

        self.label_suffix = ""


class Login_Form(_Base_Form_Config, Base_LoginForm):
    """ Form to customise the HTML & CSS generated for the login form. """

    prefix = "login"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields["login"].label = "Username / Email Address"
        self.fields["login"].widget.attrs["placeholder"] = "Enter your Username / Email Address"

        self.fields["password"].widget.attrs["placeholder"] = "Enter your Password"


class Signup_Form(_Base_Form_Config, Base_SignupForm):
    """ Form to customise the HTML & CSS generated for the signup form. """

    prefix = "signup"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields["email"].label = "Email Address"
        self.fields["email"].widget.attrs["placeholder"] = "Enter your Email Address"

        self.fields["username"].widget.attrs["placeholder"] = "Choose a Username"

        self.fields["password1"].widget.attrs["placeholder"] = "Choose a Password"

        self.fields["password2"].label = "Confirm Password"
        self.fields["password2"].widget.attrs["placeholder"] = "Re-enter your Password, to check that you can spell"

    def clean(self) -> dict[str]:
        """ Validate inserted form data using temporary in-memory user object. """

        super().clean()

        empty_fields: dict[str, bool] = {
            "username": True,
            "password": True,
            "email": True
        }
        if self.cleaned_data.get("username"):
            empty_fields["username"] = False
        if self.cleaned_data.get("password"):
            empty_fields["password"] = False
        if self.cleaned_data.get("email"):
            empty_fields["email"] = False

        try:
            get_user_model()(
                username=self.cleaned_data.get("username"),
                password=self.cleaned_data.get("password1"),
                email=self.cleaned_data.get("email")
            ).full_clean()
        except ValidationError as e:
            self.add_errors_from_ValidationError_exception(e, empty_fields)

        return self.cleaned_data

    def add_errors_from_ValidationError_exception(self, exception: ValidationError, empty_fields: dict[str, bool] = None, model_field_name: str = None) -> None:
        """
            Adds the error message(s) from any caught ValidationError exceptions
            to the forms errors dictionary/list.
        """

        if not hasattr(exception, "error_dict") and hasattr(exception, "error_list"):
            error: ValidationError
            for error in exception.error_list:
                if model_field_name and empty_fields:
                    if not empty_fields[model_field_name] and "null" in error.message:
                        self.add_error(model_field_name, error)
                elif model_field_name:
                    self.add_error(model_field_name, error)
                else:
                    self.add_error(None, error)
        elif hasattr(exception, "error_dict"):
            field_name: str
            errors: list[ValidationError]
            for field_name, errors in exception.error_dict.items():
                if field_name == "__all__":
                    self.add_error(None, errors)
                elif field_name == "password" and empty_fields:
                    if not empty_fields[field_name]:
                        self.add_error("password1", [error for error in errors if "null" not in error.message])
                elif field_name == "password":
                    self.add_error("password1", errors)
                elif empty_fields:
                    if not empty_fields[field_name]:
                        self.add_error(field_name, [error for error in errors if "null" not in error.message])
                else:
                    self.add_error(field_name, errors)
        else:
            logging.error(f"Validation error {repr(exception)} raised without a field name supplied.")


class Pulse_Form(_Base_Form_Config, forms.ModelForm):
    """ Form for creating a new Pulse """

    prefix = "create_pulse"

    # noinspection PyMissingOrEmptyDocstring
    class Meta:
        model = Pulse
        fields = ("creator", "message")
        widgets = {"creator": forms.HiddenInput}

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields["message"].label = "What are you thinking...?"
        self.fields["message"].widget.attrs["placeholder"] = "What are you thinking...?"


class Reply_Form(_Base_Form_Config, forms.ModelForm):
    """ Form for creating a new reply. """

    prefix = "create_pulse"

    # noinspection PyMissingOrEmptyDocstring
    class Meta:
        model = Reply
        fields = ("creator", "message", "_content_type", "_object_id")  # TODO: creator should be automatically assigned (not be a selectable field)
        widgets = {
            "creator": forms.HiddenInput,
            "_content_type": forms.HiddenInput,
            "_object_id": forms.HiddenInput
        }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields["message"].label = "Reply message..."
        self.fields["message"].widget.attrs["placeholder"] = "Reply message..."


class Bio_Form(_Base_Form_Config, forms.ModelForm):
    """ Form for updating a user's bio. """

    prefix = "update_bio"

    # noinspection PyMissingOrEmptyDocstring
    class Meta:
        model = get_user_model()
        fields = ("bio",)
