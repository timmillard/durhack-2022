"""
    Utility classes & functions provided for all models within this app.
"""

import logging
from random import choice as random_choice
from typing import Iterable

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldDoesNotExist
from django.db.models import DateTimeField, Field, ManyToManyField, ManyToManyRel, ManyToOneRel, Model, QuerySet

from pulsifi.exceptions import UpdateFieldNamesError

logger = logging.getLogger(__name__)


def get_random_moderator_id(excluded_moderator_id_list: list[int] = None) -> int | None:
    """ Returns a random moderator's ID. """

    ret = True
    for content_type in ContentType.objects.filter(app_label="pulsifi", model__in=settings.REPORTABLE_CONTENT_TYPE_NAMES):
        if content_type.model == "user":
            if content_type.model_class().objects.exclude(groups__name="Admins").exists():
                ret = False
        elif content_type.model_class().objects.all().exists():
            ret = False
    if ret:
        return
    if excluded_moderator_id_list:
        # noinspection PyProtectedMember
        moderator_QS: QuerySet = get_user_model().objects.filter(**apps.get_model(app_label="pulsifi", model_name="report")._meta.get_field("assigned_moderator")._limit_choices_to).exclude(id__in=excluded_moderator_id_list)
    else:
        # noinspection PyProtectedMember
        moderator_QS: QuerySet = get_user_model().objects.filter(**apps.get_model(app_label="pulsifi", model_name="report")._meta.get_field("assigned_moderator")._limit_choices_to)

    if moderator_QS.exists():
        return get_user_model().objects.get(
            id=random_choice(moderator_QS.values_list("id", flat=True))
        ).id

    raise get_user_model().DoesNotExist("Random moderator cannot be chosen, because none exist.")


class Custom_Base_Model(Model):
    """
        Base model that provides extra utility methods for all other models to
        use.

        This class is abstract so should not be instantiated or have a table
        made for it in the database (see
        https://docs.djangoproject.com/en/4.1/topics/db/models/#abstract-base-classes).
    """

    class Meta:
        abstract = True

    def base_save(self, clean=True, *args, **kwargs):
        """
            The lowest level saving function that can bypass model cleaning
            (which will usually occur if save() is called), when recursive
            saving is required (E.g. within the update() method).
        """

        if clean:
            self.full_clean()
        Model.save(self, *args, **kwargs)

    def refresh_from_db(self, using: str = None, fields: Iterable[str] = None, deep=True):
        """
            Custom implementation of refreshing in-memory objects from the
            database, which also updates any related fields on this object. The
            fields to update can be limited with the "fields" argument, and
            whether to update related objects or not can be specified with the
            "deep" argument.
        """

        super().refresh_from_db(using=using, fields=fields)

        if deep:
            model_fields: list[Field] = [model_field for model_field in self._meta.get_fields() if model_field.name != "+"]
            if fields:
                update_fields = [update_field for update_field in model_fields if update_field in fields]
            else:
                update_fields = model_fields

            if not update_fields:
                raise UpdateFieldNamesError(model_fields, fields)

            else:
                updated_model = self._meta.model.objects.get(id=self.id)

                for field in update_fields:
                    if field.is_relation and not isinstance(field, ManyToManyField) and not isinstance(field, ManyToManyRel) and not isinstance(field, GenericRelation) and not isinstance(field, ManyToOneRel):
                        """
                            It is only possible to refresh related objects from
                            one of these hard-coded field types.
                        """

                        setattr(self, field.name, getattr(updated_model, field.name))

    def save(self, *args, **kwargs):
        """
            Saves the current instance to the database, only after the model
            has been cleaned. This ensures any data in the database is valid,
            even if the data was not added via a ModelForm (E.g. data is added
            using the ORM API).
        """

        self.full_clean()
        super().save(*args, **kwargs)

    def update(self, commit=True, base_save=False, clean=True, using: str = None, **kwargs):
        """
            Changes an in-memory object's values & save that object to the
            database all in one operation (based on Django's
            Queryset.bulk_update method).
        """

        for key, value in kwargs.items():
            if key not in self.get_proxy_fields():
                try:
                    self._meta.get_field(key)
                except FieldDoesNotExist:
                    raise
            setattr(self, key, value)

        if commit:
            if base_save:
                """
                    Use the base_save method of the object (to skip additional
                    save functionality) and only clean the object if specified.
                """
                if using is not None:
                    self.base_save(clean, using)
                else:
                    self.base_save(clean)
            else:
                """ Otherwise use the normal full save method of the object. """
                if using is not None:
                    self.save(using)
                else:
                    self.save()

    @classmethod
    def get_proxy_fields(cls) -> list[str]:
        """
            Returns a list of names of extra properties of this model that can
            be saved to the database, even though those fields don't actually
            exist. They are just proxy fields.
        """

        return []


class Date_Time_Created_Base_Model(Model):
    """
        Base model that provides the field date_time_created, which is used by
        some other models in pulsifi app.

        This class is abstract so should not be instantiated or have a table
        made for it in the database (see
        https://docs.djangoproject.com/en/4.1/topics/db/models/#abstract-base-classes).
    """

    _date_time_created = DateTimeField(
        "Creation Date & Time",
        auto_now=True
    )

    @property
    def date_time_created(self):
        """
            Datetime object representing the date & time that this object
            instance was created.
        """

        return self._date_time_created

    class Meta:
        abstract = True
