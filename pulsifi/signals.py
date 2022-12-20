from allauth.account.signals import user_signed_up
from django.dispatch import receiver

from .models import Profile


def ready():
    pass


@receiver(user_signed_up)
def create_profile(request, user, **kwargs):
    Profile.objects.create(_base_user=user)