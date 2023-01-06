"""
    Utility classes & functions provided for all models within this app.
"""
import logging
from random import choice as random_choice
from typing import Iterable

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import Field, ManyToManyField, ManyToManyRel, ManyToOneRel, Model

logger = logging.getLogger(__name__)


def get_random_staff_member():
    """ Returns a random staff member's Profile. """

    if apps.get_model(app_label="pulsifi", model_name="Reply").objects.all().exists():
        staff_QS = get_user_model().objects.filter(is_staff=True)

        if staff_QS.exists():
            return get_user_model().objects.filter(
                id=random_choice(staff_QS.values_list("id", flat=True))
            ).get().id  # NOTE: Choose a random ID from the list of staff member IDs

        raise get_user_model().DoesNotExist("Random staff member cannot be chosen, because none exist in the database.")

    return None


class Custom_Base_Model(Model):
    """
        Base model that provides extra utility methods for all other models to
        use.
    """

    class Meta:  # NOTE: This class is abstract (only used for inheritance) so should not be able to be instantiated or have a table made for it in the database
        abstract = True

    def base_save(self, clean=True, *args, **kwargs):
        if clean:
            self.full_clean()
        Model.save(self, *args, **kwargs)

    def refresh_from_db(self, using: str = None, fields: Iterable[str] = None, deep=True):
        """
            Custom implementation of refreshing in-memory objects from the
            database, which also updates any related fields on this object.
        """

        super().refresh_from_db(using=using, fields=fields)  # NOTE: Update all normal fields using the base refresh_from_db method

        if deep:
            if fields:
                update_fields = [field for field in self._meta.get_fields(include_hidden=True) if field in fields and field.name != "+"]  # NOTE: Limit the fields to be updated by the ones supplied in the "fields" argument with a valid field name (not a "+")
            else:
                update_fields = [field for field in self._meta.get_fields() if field.name != "+"]  # NOTE: Limit the fields to be updated by the ones with a valid field name (not a "+")

            if not update_fields:
                if logger.getEffectiveLevel() <= logging.DEBUG:
                    logger.warning(f"""Model: {self}'s fields: {[field for field in self._meta.get_fields() if field.name != "+"]} do not overlap with refresh_from_db requested fields: {fields} """)
                else:
                    logger.warning(f"Model: {self}'s fields do not overlap with refresh_from_db requested fields")

            else:
                updated_model = self._meta.model.objects.get(id=self.id)  # NOTE: Get the updated version of the object from the database (for related fields to be replaced from)

                field: Field
                for field in update_fields:
                    if field.is_relation and not isinstance(field, ManyToManyField) and not isinstance(field, ManyToManyRel) and not isinstance(field, GenericRelation) and not isinstance(field, ManyToOneRel):  # NOTE: Limit the fields to be updated by the ones that are not a queryset of related objects
                        try:  # NOTE: Set the value of the field to be that of the corresponding field retrieved from the database
                            value = getattr(updated_model, field.name)
                        except (AttributeError, TypeError, ValueError) as e:
                            logger.error(f"Exception: {type(e).__name__} raised during refresh_from_db, when getting field: <{type(field).__name__}: {field.name}>, from model: <{type(self).__name__}: {self}>")
                        else:
                            try:
                                setattr(self, field.name, value)
                            except (AttributeError, TypeError, ValueError) as e:
                                logger.error(f"Exception: {type(e).__name__} raised during refresh_from_db, when setting field: <{type(field).__name__}: {field.name}>, of model: <{type(self).__name__}: {self}> to value: {value}")

    def save(self, *args, **kwargs):
        self.full_clean()  # NOTE: Perform full model validation before saving the object
        super().save(*args, **kwargs)

    def update(self, commit=True, base_save=False, clean=True, using: str = None, **kwargs):
        """
            Changes an in-memory object's values & save that object to the
            database all in one operation (based on Django's
            Queryset.bulk_update method).
        """

        for key, value in kwargs.items():  # NOTE: Update the values of the kwargs provided
            setattr(self, key, value)

        if commit:  # NOTE: Save the new object's state to the database as long as commit has been requested
            if base_save:  # NOTE: Use the base_save method of the model to save the object (if specified), only cleaning the object if specified
                self.base_save(clean, using)
            else:
                self.save(using)  # NOTE: Otherwise use the normal full save method of the model to save the object
