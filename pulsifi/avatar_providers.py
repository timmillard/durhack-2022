""" Adapters for use in the pulsifi app. """

from allauth.socialaccount.models import SocialAccount

from pulsifi.models import User


class DiscordAvatarProvider:
    @staticmethod
    def get_avatar_url(user: User, width: int, height: int) -> str | None:
        size = 1 << ((width * height) - 1).bit_length()
        if size > 4096:
            size = 4096
        elif size < 16:
            size = 16

        try:
            discord_SocialAccount: SocialAccount = user.socialaccount_set.get(provider="discord")
        except SocialAccount.DoesNotExist:
            return
        else:
            return f"{discord_SocialAccount.get_avatar_url()}?size={size}"
