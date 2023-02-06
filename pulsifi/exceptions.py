from typing import Iterable

from django.db.models import Field


class RedirectionLoopError(ValueError):
    DEFAULT_MESSAGE = "Redirection loop detected."  # TODO: Better default message

    def __init__(self, redirect_url: str, message: str = None) -> None:
        self.redirect_url = redirect_url
        self.message: str = message or self.DEFAULT_MESSAGE
        super().__init__(message or self.DEFAULT_MESSAGE)


class UpdateFieldNamesError(ValueError):
    DEFAULT_MESSAGE = "Model's fields does not contain any of the requested update field names."  # TODO: Better default message

    def __init__(self, model_fields: Iterable[Field], update_field_names: Iterable[str], message: str = None) -> None:
        self.model_fields = model_fields
        self.update_field_names = update_field_names
        self.message: str = message or self.DEFAULT_MESSAGE
        super().__init__(message or self.DEFAULT_MESSAGE)
