"""
    Automated test suite for concrete models in pulsifi app.
"""
import copy

from django.db.models import BooleanField
from django.test import TestCase

from pulsifi.models import BaseUser, Profile
from pulsifi.tests.utils import CreateTestProfileHelper, GetFieldsHelper


# TODO: tests docstrings


class Profile_Model_Tests(TestCase):
    def test_refresh_from_database_updates_non_relation_fields(self):
        profile = CreateTestProfileHelper.create_test_profile()
        old_profile = Profile.objects.get(id=profile.id)

        self.assertEqual(profile, old_profile)

        for field in GetFieldsHelper.get_non_relation_fields(profile, exclude=["id"]):
            if field.name in CreateTestProfileHelper.TEST_PROFILES[0]:
                setattr(
                    profile,
                    field.name,
                    CreateTestProfileHelper.get_test_unknown_field(field.name)
                )
            elif isinstance(field, BooleanField):
                setattr(profile, field.name, not getattr(profile, field.name))

            self.assertNotEqual(
                getattr(profile, field.name),
                getattr(old_profile, field.name)
            )

            profile.refresh_from_db()
            self.assertEqual(
                getattr(profile, field.name),
                getattr(old_profile, field.name)
            )

    def test_base_user_shortcut_and_delete_makes_Null_BaseUser_object(self):
        profile = CreateTestProfileHelper.create_test_profile()

        self.assertIsInstance(profile.base_user, BaseUser)

        profile.base_user.delete()
        profile.refresh_from_db()

        self.assertIsInstance(profile.base_user, Profile._Null_BaseUser)

    def test_base_user_attribute_shortcuts(self):
        profile = CreateTestProfileHelper.create_test_profile()

        self.assertEqual(profile.username, profile.base_user.username)
        self.assertEqual(profile.email, profile.base_user.email)
        self.assertEqual(profile.date_joined, profile.base_user.date_joined)
        self.assertEqual(profile.visible, profile.base_user.is_active)
        self.assertEqual(
            profile.emailaddress_set,
            profile.base_user.emailaddress_set
        )
        self.assertEqual(profile.visible, profile.base_user.is_active)

        profile.base_user.delete()
        profile.refresh_from_db()

        if isinstance(profile.base_user, Profile._Null_BaseUser) and not profile.base_user:
            self.assertEqual(profile.visible, profile.base_user.is_active)
            self.assertFalse(profile.visible)

    def test_shortcut_username_setter_with_base_user(self):
        profile = CreateTestProfileHelper.create_test_profile()
        old_profile = copy.deepcopy(profile)
        profile.username = CreateTestProfileHelper.get_test_unknown_field("username")

        self.assertNotEqual(profile.username, old_profile.username)

    def test_shortcut_email_setter_with_base_user(self):
        profile = CreateTestProfileHelper.create_test_profile()
        old_profile = copy.deepcopy(profile)

        profile.email = CreateTestProfileHelper.get_test_unknown_field("email")

        self.assertNotEqual(profile.email, old_profile.email)

    def test_shortcut_email_setter_with_base_user_with_email_already_exists(self):
        # noinspection SpellCheckingInspection
        CreateTestProfileHelper.create_test_profile(email="testemail@example.com")
        profile = CreateTestProfileHelper.create_test_profile()

        with self.assertRaises(ValueError):
            profile.email = "testemail@example.com"

    def test_shortcut_visible_setter_with_base_user(self):
        pass

    def test_shortcut_visible_setter_without_base_user(self):
        pass

    def test_stringify_displays_in_correct_format(self):
        profile = CreateTestProfileHelper.create_test_profile()

        self.assertEqual(str(profile), f"@{profile.base_user.username}")

        profile.update(visible=False)

        self.assertEqual(
            str(profile),
            "".join(letter + "\u0336" for letter in f"@{profile.base_user.username}")
        )

    def test_nonactive_base_user_makes_profile_not_visible(self):
        profile = CreateTestProfileHelper.create_test_profile()

        self.assertTrue(profile.base_user.is_active)
        self.assertTrue(profile.visible)

        profile.base_user.is_active = False
        profile.base_user.save()

        profile.save()

        self.assertFalse(profile.base_user.is_active)
        self.assertFalse(profile.visible)

    def test_not_visible_profile_makes_base_user_nonactive(self):
        profile = CreateTestProfileHelper.create_test_profile()

        self.assertTrue(profile.visible)
        self.assertTrue(profile.base_user.is_active)

        profile.update(visible=False)

        self.assertFalse(profile.visible)
        self.assertFalse(profile.base_user.is_active)


class _User_Generated_Content_Model(TestCase):
    pass
