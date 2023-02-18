from typing import Collection

from django.db.models import Field


class RedirectionLoopError(ValueError):
    """
        Provided URL redirects to a location that refers to this URL. Results
        in a redirection loop.
    """

    DEFAULT_MESSAGE = "Redirection loop detected."  # TODO: Better default message

    def __init__(self, message: str = None, redirect_url: str = None) -> None:
        self.message: str = message or self.DEFAULT_MESSAGE
        self.redirect_url = redirect_url
        super().__init__(message or self.DEFAULT_MESSAGE)

    def __str__(self) -> str:
        """ Returns formatted message & properties of the RedirectionLoopError. """

        return f"{self.message} (redirect_url={repr(self.redirect_url)})"


class UpdateFieldNamesError(ValueError):
    """
        Provided field names do not match any of the fields within the given
        model.
    """

    DEFAULT_MESSAGE = "Model's fields does not contain any of the requested update field names."  # TODO: Better default message

    def __init__(self, message: str = None, model_fields: Collection[Field] = None, update_field_names: Collection[str] = None) -> None:
        self.message: str = message or self.DEFAULT_MESSAGE

        if model_fields is None:
            self.model_fields = set()
        else:
            self.model_fields = set(model_fields)

        if update_field_names is None:
            self.update_field_names = set()
        else:
            self.update_field_names = set(update_field_names)

        super().__init__(message or self.DEFAULT_MESSAGE)

    def __str__(self) -> str:
        """
            Returns formatted message & properties of the
            UpdateFieldNamesError.
        """

        return f"{self.message} (model_fields={repr(self.model_fields)}, update_field_names={repr(self.update_field_names)})"


class GetParameterError(ValueError):
    """ Provided get parameters in HTTP request contain an invalid value. """

    DEFAULT_MESSAGE = "One or more of the supplied Get parameters have an invalid value."

    def __init__(self, message: str = None, get_parameters: dict[str, str] = None) -> None:
        self.message: str = message or self.DEFAULT_MESSAGE

        if get_parameters is None:
            self.get_parameters = {}
        else:
            self.get_parameters = get_parameters

        super().__init__(message or self.DEFAULT_MESSAGE)

    def __str__(self) -> str:
        """ Returns formatted message & properties of the GetParameterError. """

        return f"{self.message} (get_parameters={repr(self.get_parameters)})"


class ReportableContentTypeNamesSettingError(ValueError):
    """
        Provided REPORTABLE_CONTENT_TYPE_NAMES contains a value that is not a
        valid model name.
    """

    DEFAULT_MESSAGE = "One of the supplied REPORTABLE_CONTENT_TYPE_NAMES is not a valid model name."

    def __init__(self, message: str = None, reportable_content_type_name: str = None) -> None:
        self.message: str = message or self.DEFAULT_MESSAGE
        self.reportable_content_type_name = reportable_content_type_name

        super().__init__(message or self.DEFAULT_MESSAGE)

    def __str__(self) -> str:
        """ Returns formatted message & properties of the GetParameterError. """

        return f"{self.message} (reportable_content_type_name={repr(self.reportable_content_type_name)})"
