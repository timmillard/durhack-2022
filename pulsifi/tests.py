"""
    Automated test suite for pulsifi application & core.
"""

from django.test import TestCase

from .models import BaseUser, Profile


class CreateTestProfileMixin:
    @staticmethod
    def create_test_profile():
        return Profile.objects.create(
            _base_user=BaseUser.objects.create_user(
                username="padgriffin",
                password="#2@cqt*2A8R5ZX",
                email="padgriffin@gmail.com"
            ),
            name="Pad Griffin"
        )


class Profile_Model_Tests(CreateTestProfileMixin, TestCase):
    def test_stringify_displays_in_correct_format(self):
        profile = self.create_test_profile()

        self.assertEqual(str(profile), f"@{profile.base_user.username}")

        profile.update(visible=False)

        self.assertEqual(str(profile), "".join(letter + "\u0336" for letter in f"@{profile.base_user.username}"))

    def test_nonactive_base_user_makes_profile_not_visible(self):
        profile = self.create_test_profile()

        self.assertEqual(profile.base_user.is_active, True)
        self.assertEqual(profile.visible, True)

        profile.base_user.is_active = False
        profile.base_user.save()

        profile.save()

        self.assertEqual(profile.base_user.is_active, False)
        self.assertEqual(profile.visible, False)

    def test_not_visible_profile_makes_base_user_nonactive(self):
        profile = self.create_test_profile()

        self.assertEqual(profile.visible, True)
        self.assertEqual(profile.base_user.is_active, True)

        profile.update(visible=False)

        self.assertEqual(profile.visible, False)
        self.assertEqual(profile.base_user.is_active, False)