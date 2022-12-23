"""
    Automated test suite for pulsifi application & core.
"""

from django.test import TestCase

from .models import BaseUser, Profile


class CreateTestProfileMixin:
    TEST_PROFILES = [
        {"username": "padgriffin", "password": "#2@cqt", "email": "padgriffin@gmail.com"},  # noqa
        {"username": "Extralas55", "password": "321321", "email": "green.anna@hotmail.co.uk"},  # noqa
        {"username": "Rines1970", "password": "chicken1", "email": "robyn1973@yahoo.com"},  # noqa
        {"username": "Requit", "password": "pa55word", "email": "alexander.griffiths@shaw.com"},  # noqa
        {"username": "Nionothe", "password": "turnedrealizeroyal", "email": "pjackpppson@stewart.com"},  # noqa
        {"username": "neha_schumm", "password": "1q2w3e4r", "email": "iyoung@gmail.com"},  # noqa
        {"username": "Myseat59", "password": "password", "email": "viva_konopels@hotmail.com"},  # noqa
        {"username": "Tunt1978", "password": "OoYoa9ahf", "email": "rachael2001@gmail.com"},  # noqa
        {"username": "eesait4Oo", "password": "323232", "email": "julia_scott99@reynolds.com"},  # noqa
        {"username": "Therhatim", "password": "JORDAN", "email": "ken80@jones.net"},  # noqa
        {"username": "Repostity", "password": "aequei3Eequ", "email": "simpson.mark@clark.co.uk"},  # noqa
        {"username": "Proodents445", "password": "teddybea", "email": "AlfieOsborne@dayrep.com"},  # noqa
        {"username": "Hassaid", "password": "vh5150", "email": "holly65@gmail.com"},  # noqa
        {"username": "alexzander", "password": "PulsifiPass123", "email": "khan.imogen@gmail.com"},  # noqa
        {"username": "annalise", "password": "24101984", "email": "jessica.price@outlook.com"},  # noqa
        {"username": "walter.her1992", "password": "18atcskd2w", "email": "christian40@bell.biz"},  # noqa
        {"username": "rodger.nader", "password": "letmein", "email": "norene.nikola@gmail.com"},  # noqa
        {"username": "lorenz._fri1988", "password": "monkey", "email": "Exielenn@studentmail.net"},  # noqa
        {"username": "grayson", "password": "Iloveyou", "email": "gus2017@hotmail.com"},  # noqa
        {"username": "Professor_T", "password": "lung-calf-trams", "email": "trofessor_t@trofessor_t.com"}  # noqa
    ]
    _test_profile_index = -1

    def create_test_profile(self):
        self._test_profile_index = (self._test_profile_index + 1) % len(self.TEST_PROFILES)
        return Profile.objects.create(
            _base_user=BaseUser.objects.create_user(
                username=self.TEST_PROFILES[self._test_profile_index]["username"],
                password=self.TEST_PROFILES[self._test_profile_index]["password"],
                email=self.TEST_PROFILES[self._test_profile_index]["email"]
            )
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
