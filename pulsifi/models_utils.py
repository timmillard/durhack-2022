"""
    Utility classes & functions provided for all models within this app.
"""

import logging
from random import choice as random_choice
from typing import Iterable

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models import DateTimeField, Field, ManyToManyField, ManyToManyRel, ManyToOneRel, Model, QuerySet

logger = logging.getLogger(__name__)


def get_random_staff_member_id(excluded_staff_id_list: list[int] = None) -> int | None:
    """ Returns a random staff member's ID. """

    ret = True
    for content_type in ContentType.objects.filter(app_label="pulsifi", model__in=("user", "pulse", "reply")):
        if content_type.model == "user":
            if content_type.model_class().objects.exclude(groups__name="Admins").exists():
                ret = False
        elif content_type.model_class().objects.all().exists():
            ret = False
    if ret:
        return
    if excluded_staff_id_list:
        # noinspection PyProtectedMember
        staff_QS: QuerySet = get_user_model().objects.filter(**apps.get_model(app_label="pulsifi", model_name="report")._meta.get_field("assigned_staff_member")._limit_choices_to).exclude(id__in=excluded_staff_id_list)
    else:
        # noinspection PyProtectedMember
        staff_QS: QuerySet = get_user_model().objects.filter(**apps.get_model(app_label="pulsifi", model_name="report")._meta.get_field("assigned_staff_member")._limit_choices_to)

    if staff_QS.exists():
        return get_user_model().objects.get(
            id=random_choice(staff_QS.values_list("id", flat=True))
        ).id

    raise get_user_model().DoesNotExist("Random staff member cannot be chosen, because none exist.")


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
            if fields:
                update_fields = [field for field in self._meta.get_fields(include_hidden=True) if field in fields and field.name != "+"]
            else:
                update_fields = [field for field in self._meta.get_fields() if field.name != "+"]

            if not update_fields:
                if logger.getEffectiveLevel() <= logging.DEBUG:
                    logger.warning(f"""Model: {self}'s fields: {[field for field in self._meta.get_fields() if field.name != "+"]} do not overlap with refresh_from_db requested fields: {fields} """)
                else:
                    logger.warning(f"Model: {self}'s fields do not overlap with refresh_from_db requested fields")

            else:
                updated_model = self._meta.model.objects.get(id=self.id)

                field: Field
                for field in update_fields:
                    if field.is_relation and not isinstance(field, ManyToManyField) and not isinstance(field, ManyToManyRel) and not isinstance(field, GenericRelation) and not isinstance(field, ManyToOneRel):
                        """
                            It is only possible to refresh related objects from
                            one of these hard-coded field types.
                        """

                        try:
                            value = getattr(updated_model, field.name)
                        except (AttributeError, TypeError, ValueError) as e:
                            logger.error(f"Exception: {type(e).__name__} raised during refresh_from_db, when getting field: <{type(field).__name__}: {field.name}>, from model: <{type(self).__name__}: {self}>")
                        else:
                            try:
                                setattr(self, field.name, value)
                            except (AttributeError, TypeError, ValueError) as e:
                                logger.error(f"Exception: {type(e).__name__} raised during refresh_from_db, when setting field: <{type(field).__name__}: {field.name}>, of model: <{type(self).__name__}: {self}> to value: {value}")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def update(self, commit=True, base_save=False, clean=True, using: str = None, **kwargs):
        """
            Changes an in-memory object's values & save that object to the
            database all in one operation (based on Django's
            Queryset.bulk_update method).
        """

        for key, value in kwargs.items():
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


class Date_Time_Created_Base_Model(Model):
    """


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
        return self._date_time_created

    class Meta:
        abstract = True
