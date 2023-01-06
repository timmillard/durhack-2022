"""
    Automated test suite for concrete models in pulsifi app.
"""

from django.contrib.auth import get_user_model
from django.db.models import BooleanField
from django.test import TestCase

from pulsifi.tests.utils import CreateTestUserHelper, GetFieldsHelper


# TODO: tests docstrings


class User_Model_Tests(TestCase):
    def test_refresh_from_database_updates_non_relation_fields(self):
        user = CreateTestUserHelper.create_test_user()
        old_user = get_user_model().objects.get(id=user.id)

        self.assertEqual(user, old_user)

        for field in GetFieldsHelper.get_non_relation_fields(user, exclude=["id", "last_login", "date_joined"]):
            if field.name in CreateTestUserHelper.TEST_USERS[0]:
                setattr(
                    user,
                    field.name,
                    CreateTestUserHelper.get_test_unknown_field(field.name)
                )
            elif isinstance(field, BooleanField):
                setattr(user, field.name, not getattr(user, field.name))

            self.assertNotEqual(
                getattr(user, field.name),
                getattr(old_user, field.name)
            )

            user.refresh_from_db()
            self.assertEqual(
                getattr(user, field.name),
                getattr(old_user, field.name)
            )

    def test_delete_makes_not_active(self):
        user = CreateTestUserHelper.create_test_user()

        self.assertTrue(user.is_active)

        user.delete()
        user.refresh_from_db()

        self.assertFalse(user.is_active)

    def test_visible_shortcut(self):
        user = CreateTestUserHelper.create_test_user()

        self.assertEqual(user.visible, user.is_active)

        user.visible = False

        self.assertEqual(user.visible, user.is_active)

    def test_stringify_displays_in_correct_format(self):
        user = CreateTestUserHelper.create_test_user()

        self.assertEqual(str(user), f"@{user.username}")

        user.update(is_active=False)

        self.assertEqual(
            str(user),
            "".join(letter + "\u0336" for letter in f"@{user.username}")
        )


class _User_Generated_Content_Model(TestCase):
    pass
