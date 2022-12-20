from allauth.account.signals import user_signed_up
from django.core.handlers.wsgi import WSGIRequest
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import BaseUser, Profile


def ready():
    pass


@receiver(user_signed_up)
def create_profile(request: WSGIRequest, user: BaseUser, **kwargs):
    Profile.objects.create(_base_user=user)

@receiver(pre_save, sender=BaseUser)
def clear_first_last_names(sender: object, instance: BaseUser, **kwargs):
    if instance.first_name != "":
        instance.first_name = ""
    if instance.last_name != "":
        instance.last_name = ""