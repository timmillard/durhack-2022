""" Adapters for use in the pulsifi app. """

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount

from pulsifi.models import User


class Custom_Pulsifi_SocialAccountAdapter(DefaultSocialAccountAdapter):
    # noinspection SpellCheckingInspection
    def populate_user(self, request, sociallogin: SocialAccount, data: dict[str, ...]) -> User:
        print("here")
        print(sociallogin)
        print(sociallogin.get_avatar_url())
        return super().populate_user(request, sociallogin, data)
