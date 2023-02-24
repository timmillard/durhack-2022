"""
    Utility classes & functions provided for all models within this app.
"""

from random import choice as random_choice
from typing import Collection, Iterable

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import FieldDoesNotExist
from django.db.models import DateTimeField, Field, ManyToManyField, ManyToManyRel, ManyToOneRel, Model, QuerySet

from pulsifi.exceptions import UpdateFieldNamesError


def get_random_moderator_id(excluded_moderator_ids: Iterable[int] = None) -> int | None:
    """
        Returns a random moderator's ID. (Returns None if no moderators and no
        reportable objects exist).
    """

    ret = True
    for model_name in settings.REPORTABLE_CONTENT_TYPE_NAMES:
        if model_name == "user":
            if apps.get_model(app_label="pulsifi", model_name=model_name).objects.exclude(groups__name="Admins").exists():
                ret = False
        elif apps.get_model(app_label="pulsifi", model_name=model_name).objects.all().exists():
            ret = False
    if ret:
        return  # HACK: Return None rather than raising an exception if no reportable objects exist. This prevents crashing during initialisation, as this function is parsed before reportable objects have been loaded (which would normally cause a crash)

    if excluded_moderator_ids:
        # noinspection PyProtectedMember
        moderator_QS: QuerySet = get_user_model().objects.filter(**apps.get_model(app_label="pulsifi", model_name="report")._meta.get_field("assigned_moderator")._limit_choices_to).exclude(id__in=excluded_moderator_ids)
    else:
        # noinspection PyProtectedMember
        moderator_QS: QuerySet = get_user_model().objects.filter(**apps.get_model(app_label="pulsifi", model_name="report")._meta.get_field("assigned_moderator")._limit_choices_to)

    NO_MODERATORS_EXIST_ERROR = "Random moderator cannot be chosen, because none exist."
    try:
        return get_user_model().objects.get(
            id=random_choice(moderator_QS.values_list("id", flat=True))
        ).id
    except get_user_model().DoesNotExist as e:
        e.args = (NO_MODERATORS_EXIST_ERROR,)
        raise e
    except IndexError as e:
        raise get_user_model().DoesNotExist(NO_MODERATORS_EXIST_ERROR) from e


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

    def base_save(self, clean=True, *args, **kwargs) -> None:
        """
            The lowest level saving function that can bypass model cleaning
            (which will usually occur if save() is called), when recursive
            saving is required (E.g. within the update() method).
        """

        if clean:
            self.full_clean()

        Model.save(self, *args, **kwargs)

    def refresh_from_db(self, using: str = None, fields: Collection[str] = None, deep=True) -> None:
        """
            Custom implementation of refreshing in-memory objects from the
            database, which also updates any related fields on this object. The
            fields to update can be limited with the "fields" argument, and
            whether to update related objects or not can be specified with the
            "deep" argument.
        """

        if fields is not None and not isinstance(fields, set):  # NOTE: Remove duplicate field names from fields parameter
            fields = set(fields)

        super().refresh_from_db(using=using, fields=fields)

        if fields is None:
            fields = set()

        if deep:  # NOTE: Refresh any related fields/objects if requested
            model_fields: set[Field] = {model_field for model_field in self._meta.get_fields() if model_field.name != "+"}

            if fields:  # NOTE: Limit the fields to update by the provided list of field names
                update_fields: set[Field] = {update_field for update_field in model_fields if update_field.name in fields}
            else:
                update_fields = model_fields

            if not update_fields:  # NOTE: Raise exception if none of the provided field names are valid fields for this model
                raise UpdateFieldNamesError(model_fields=model_fields, update_field_names=fields)

            else:
                updated_model = self._meta.model.objects.get(id=self.id)

                for field in update_fields:
                    if field.is_relation and not isinstance(field, ManyToManyField) and not isinstance(field, ManyToManyRel) and not isinstance(field, GenericRelation) and not isinstance(field, ManyToOneRel):  # NOTE: It is only possible to refresh related objects from one of these hard-coded field types
                        setattr(self, field.name, getattr(updated_model, field.name))

                    elif field.is_relation:  # BUG: Relation fields not of acceptable type are not refreshed
                        pass

    def save(self, *args, **kwargs) -> None:
        """
            Saves the current instance to the database, only after the model
            has been cleaned. This ensures any data in the database is valid,
            even if the data was not added via a ModelForm (E.g. data is added
            using the ORM API).
        """

        self.full_clean()

        super().save(*args, **kwargs)

    def update(self, commit=True, base_save=False, clean=True, using: str = None, **kwargs) -> None:
        """
            Changes an in-memory object's values & save that object to the
            database all in one operation (based on Django's
            Queryset.bulk_update method).
        """

        key: str
        for key, value in kwargs.items():
            if key not in self.get_proxy_field_names():  # NOTE: Given field name must be a proxy field name or an actual field name
                try:
                    self._meta.get_field(key)
                except FieldDoesNotExist:
                    raise
            setattr(self, key, value)

        if commit:
            if base_save:  # NOTE: Use the base_save method of the object (to skip additional save functionality) and only clean the object if specified
                if using is not None:
                    self.base_save(clean, using)
                else:
                    self.base_save(clean)

            else:  # NOTE: Otherwise use the normal full save method of the object
                if using is not None:
                    self.save(using)
                else:
                    self.save()

    @staticmethod
    def get_proxy_field_names() -> set[str]:
        """
            Returns a set of names of extra properties of this model that can
            be saved to the database, even though those fields don't actually
            exist. They are just proxy fields.
        """

        return set()


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
        auto_now=True,
        help_text="Datetime object representing the date & time that this object instance was created."
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
