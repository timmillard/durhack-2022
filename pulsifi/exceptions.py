from typing import Collection

from django.db.models import Field


class RedirectionLoopError(ValueError):
    DEFAULT_MESSAGE = "Redirection loop detected."  # TODO: Better default message

    def __init__(self, message: str = None, redirect_url: str = None) -> None:
        self.message: str = message or self.DEFAULT_MESSAGE
        self.redirect_url = redirect_url
        super().__init__(message or self.DEFAULT_MESSAGE)


class UpdateFieldNamesError(ValueError):
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


class GetParameterError(ValueError):
    DEFAULT_MESSAGE = "One or more of the supplied Get parameters have an invalid value."

    def __init__(self, message: str = None, get_parameters: dict[str, str] = None) -> None:
        self.message: str = message or self.DEFAULT_MESSAGE

        if get_parameters is None:
            self.get_parameters = {}
        else:
            self.get_parameters = get_parameters

        super().__init__(message or self.DEFAULT_MESSAGE)
