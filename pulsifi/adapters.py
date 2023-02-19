""" Adapters for use in the pulsifi app. """

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class Custom_Pulsifi_SocialAccountAdapter(DefaultSocialAccountAdapter):
    # noinspection SpellCheckingInspection
    def populate_user(self, request, sociallogin, data):
        print("here")
        return super().populate_user(request, sociallogin, data)
