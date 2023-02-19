""" Adapters for use in the pulsifi app. """

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialLogin

from pulsifi.models import User


class Custom_Pulsifi_SocialAccountAdapter(DefaultSocialAccountAdapter):
    # noinspection SpellCheckingInspection
    def populate_user(self, request, sociallogin: SocialLogin, data: dict[str, ...]) -> User:
        print("here")
        print(sociallogin)
        print(sociallogin.account.get_avatar_url())
        return super().populate_user(request, sociallogin, data)
