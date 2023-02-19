""" Adapters for use in the pulsifi app. """
import logging

from allauth.socialaccount.models import SocialAccount

from pulsifi.models import User


class DiscordAvatarProvider:
    @staticmethod
    def get_avatar_url(user: User, width: int, height: int) -> str | None:
        logging.debug(user, width, height)
        # logging.debug(1 << ((width * height) - 1).bit_length())
        try:
            discord_SocialAccount: SocialAccount = user.socialaccount_set.get(provider="discord")
        except user.socialaccount_set.DoesNotExist:
            return
        else:
            return f"{discord_SocialAccount.get_avatar_url()}?size={1 << ((width * height) - 1).bit_length()}"
