"""
    Automated test suite for abstract models in pulsifi app.
"""
import copy

from django.test import TestCase

from pulsifi.models import BaseUser, Profile, get_random_staff_member
from pulsifi.tests.utils import CreateTestProfileHelper, CreateTestUserGeneratedContentHelper, DeleteBaseUserHelper


# TODO: tests docstrings

class Get_Random_Staff_Member_Util_Function_Tests(TestCase):
    def test_get_random_staff_member_with_no_Replies(self):
        self.assertIsNone(get_random_staff_member())

    def test_get_random_staff_member_with_Replies_and_no_staff_members(self):
        CreateTestUserGeneratedContentHelper.create_test_reply()

        # noinspection PyTypeChecker
        with self.assertRaises(Profile.DoesNotExist):
            get_random_staff_member()

    def test_get_random_staff_member_with_Replies_and_staff_members(self):
        pass


class Custom_Base_Model_Tests(TestCase):
    pass


class Visible_Reportable_Model_Tests(TestCase):
    def test_string_when_visible(self):
        pass


class Null_BaseUser_Tests(TestCase):
    @classmethod
    def create_Null_BaseUser(cls) -> Profile._Null_BaseUser:
        profile = CreateTestProfileHelper.create_test_profile()
        profile.base_user.delete()
        profile.refresh_from_db()
        return profile.base_user

    def test_bool_is_False(self):
        profile = CreateTestProfileHelper.create_test_profile()

        self.assertTrue(profile.base_user)

        profile = DeleteBaseUserHelper.delete_base_user(profile)

        self.assertFalse(profile.base_user)

    def test_visibility_is_False(self):
        profile = CreateTestProfileHelper.create_test_profile()

        self.assertTrue(profile.visible)
        self.assertTrue(profile.base_user.is_active)
        self.assertTrue(profile.base_user.is_authenticated)
        self.assertFalse(profile.base_user.is_anonymous)

        profile = DeleteBaseUserHelper.delete_base_user(profile)

        self.assertFalse(profile.visible)
        self.assertFalse(profile.base_user.is_active)
        self.assertFalse(profile.base_user.is_authenticated)
        self.assertTrue(profile.base_user.is_anonymous)

    def test_constants_return_BaseUser_constants(self):
        CONSTANT_NAMES = ["USERNAME_FIELD", "EMAIL_FIELD", "REQUIRED_FIELDS"]

        # noinspection SpellCheckingInspection
        null_baseuser = self.create_Null_BaseUser()

        for constant in CONSTANT_NAMES:
            self.assertEqual(
                getattr(null_baseuser, constant),
                getattr(BaseUser, constant)
            )

    def test_exceptions_inherit_BaseUser_exceptions(self):
        EXCEPTION_NAMES = ["DoesNotExist", "MultipleObjectsReturned"]

        # noinspection SpellCheckingInspection
        null_baseuser = self.create_Null_BaseUser()

        for exception in EXCEPTION_NAMES:
            self.assertTrue(
                issubclass(
                    getattr(null_baseuser, exception),
                    getattr(BaseUser, exception)
                )
            )

    def test_attempt_get_main_attributes_raises_DoesNotExist(self):
        PROFILE_ATTRIBUTE_NAMES = ["username", "email", "date_joined"]
        # noinspection SpellCheckingInspection
        BASEUSER_ATTRIBUTE_NAMES = [
            "username",
            "email",
            "password",
            "is_staff",
            "is_superuser",
            "id",
            "last_login",
            "date_joined",
            "_meta",
            "_state",
            "pk"
        ]
        profile = CreateTestProfileHelper.create_test_profile()

        for attribute_name in PROFILE_ATTRIBUTE_NAMES:
            try:
                getattr(profile, attribute_name)

            except BaseUser.DoesNotExist:
                if profile.base_user or isinstance(profile.base_user, Profile._Null_BaseUser):
                    self.fail(f"Accessing {attribute_name} on BaseUser object <{profile.base_user}> via Profile raised BaseUser.DoesNotExist")
                else:
                    self.fail(f"Accessing {attribute_name} on BaseUser object <profile.base_user> via Profile raised BaseUser.DoesNotExist")

            try:
                if attribute_name != "date_joined":
                    setattr(copy.deepcopy(profile), attribute_name, "value")

            except BaseUser.DoesNotExist:
                if profile.base_user or isinstance(profile.base_user, Profile._Null_BaseUser):
                    self.fail(f"Setting {attribute_name} on BaseUser object <{profile.base_user}> via Profile raised BaseUser.DoesNotExist")
                else:
                    self.fail(f"Setting {attribute_name} on BaseUser object <profile.base_user> via Profile raised BaseUser.DoesNotExist")

        for attribute_name in BASEUSER_ATTRIBUTE_NAMES:
            try:
                getattr(profile.base_user, attribute_name)

            except BaseUser.DoesNotExist:
                if profile.base_user or isinstance(profile.base_user, Profile._Null_BaseUser):
                    self.fail(f"Accessing {attribute_name} on BaseUser object: <{profile.base_user}> raised BaseUser.DoesNotExist")
                else:
                    self.fail(f"Accessing {attribute_name} on BaseUser object: <profile.base_user> raised BaseUser.DoesNotExist")

            try:
                setattr(
                    copy.deepcopy(profile).base_user,
                    attribute_name, "value"
                )

            except BaseUser.DoesNotExist:
                if profile.base_user or isinstance(profile.base_user, Profile._Null_BaseUser):
                    self.fail(f"Setting {attribute_name} on BaseUser object: <{profile.base_user}> raised BaseUser.DoesNotExist")
                else:
                    self.fail(f"Setting {attribute_name} on BaseUser object: <profile.base_user> raised BaseUser.DoesNotExist")

        profile = DeleteBaseUserHelper.delete_base_user(profile)

        for attribute_name in PROFILE_ATTRIBUTE_NAMES:
            # noinspection PyTypeChecker
            with self.assertRaises(BaseUser.DoesNotExist, msg=f"PROFILE_ATTRIBUTES, get attribute_name={attribute_name}"):
                getattr(profile, attribute_name)

            if attribute_name == "username":
                # noinspection PyTypeChecker
                with self.assertRaises(BaseUser.DoesNotExist, msg=f"PROFILE_ATTRIBUTES, set attribute_name={attribute_name}"):
                    setattr(copy.deepcopy(profile), attribute_name, "value")
            elif attribute_name != "date_joined":
                try:
                    setattr(copy.deepcopy(profile), attribute_name, "value")

                except BaseUser.DoesNotExist:
                    if profile.base_user or isinstance(profile.base_user, Profile._Null_BaseUser):
                        self.fail(f"Setting {attribute_name} on BaseUser object <{profile.base_user}> via Profile raised BaseUser.DoesNotExist")
                    else:
                        self.fail(f"Setting {attribute_name} on BaseUser object <profile.base_user> via Profile raised BaseUser.DoesNotExist")

        for attribute_name in BASEUSER_ATTRIBUTE_NAMES:
            # noinspection PyTypeChecker, SpellCheckingInspection
            with self.assertRaises(BaseUser.DoesNotExist, msg=f"BASEUSER_ATTRIBUTES, get attribute_name={attribute_name}"):
                getattr(profile.base_user, attribute_name)

            # noinspection PyTypeChecker, SpellCheckingInspection
            with self.assertRaises(BaseUser.DoesNotExist, msg=f"BASEUSER_ATTRIBUTES, set attribute_name={attribute_name}"):
                setattr(
                    copy.deepcopy(profile).base_user,
                    attribute_name,
                    "value"
                )
