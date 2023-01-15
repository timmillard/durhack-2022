"""
    Automated test suite for concrete models in pulsifi app.
"""

from django.contrib.auth import get_user_model
from django.db.models import BooleanField
from django.test import TestCase

from pulsifi.tests.utils import CreateTestUserGeneratedContentHelper, CreateTestUserHelper, GetFieldsHelper


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

    def test_reverse_liked_pulse_becoming_disliked_removes_like(self):
        user1 = CreateTestUserHelper.create_test_user()
        user2 = CreateTestUserHelper.create_test_user()
        pulse = CreateTestUserGeneratedContentHelper.create_test_pulse(creator=user1)

        user2.liked_pulse_set.add(pulse)

        self.assertTrue(pulse.liked_by.filter(id=user2.id).exists())
        self.assertFalse(pulse.disliked_by.filter(id=user2.id).exists())

        user2.disliked_pulse_set.add(pulse)

        self.assertTrue(pulse.disliked_by.filter(id=user2.id).exists())
        self.assertFalse(pulse.liked_by.filter(id=user2.id).exists())

    def test_reverse_disliked_pulse_becoming_liked_removes_dislike(self):
        user1 = CreateTestUserHelper.create_test_user()
        user2 = CreateTestUserHelper.create_test_user()
        pulse = CreateTestUserGeneratedContentHelper.create_test_pulse(creator=user1)

        user2.disliked_pulse_set.add(pulse)

        self.assertTrue(pulse.disliked_by.filter(id=user2.id).exists())
        self.assertFalse(pulse.liked_by.filter(id=user2.id).exists())

        user2.liked_pulse_set.add(pulse)

        self.assertTrue(pulse.liked_by.filter(id=user2.id).exists())
        self.assertFalse(pulse.disliked_by.filter(id=user2.id).exists())

    def test_reverse_liked_reply_becoming_disliked_removes_like(self):
        user1 = CreateTestUserHelper.create_test_user()
        user2 = CreateTestUserHelper.create_test_user()
        reply = CreateTestUserGeneratedContentHelper.create_test_reply(creator=user1)

        user2.liked_reply_set.add(reply)

        self.assertTrue(reply.liked_by.filter(id=user2.id).exists())
        self.assertFalse(reply.disliked_by.filter(id=user2.id).exists())

        user2.disliked_reply_set.add(reply)

        self.assertTrue(reply.disliked_by.filter(id=user2.id).exists())
        self.assertFalse(reply.liked_by.filter(id=user2.id).exists())

    def test_reverse_disliked_reply_becoming_liked_removes_dislike(self):
        user1 = CreateTestUserHelper.create_test_user()
        user2 = CreateTestUserHelper.create_test_user()
        reply = CreateTestUserGeneratedContentHelper.create_test_reply(creator=user1)

        user2.disliked_reply_set.add(reply)

        self.assertTrue(reply.disliked_by.filter(id=user2.id).exists())
        self.assertFalse(reply.liked_by.filter(id=user2.id).exists())

        user2.liked_reply_set.add(reply)

        self.assertTrue(reply.liked_by.filter(id=user2.id).exists())
        self.assertFalse(reply.disliked_by.filter(id=user2.id).exists())


class _User_Generated_Content_Model(TestCase):
    def test_liked_pulse_becoming_disliked_removes_like(self):
        user1 = CreateTestUserHelper.create_test_user()
        user2 = CreateTestUserHelper.create_test_user()
        pulse = CreateTestUserGeneratedContentHelper.create_test_pulse(creator=user1)

        pulse.liked_by.add(user2)

        self.assertTrue(pulse.liked_by.filter(id=user2.id).exists())
        self.assertFalse(pulse.disliked_by.filter(id=user2.id).exists())

        pulse.disliked_by.add(user2)

        self.assertTrue(pulse.disliked_by.filter(id=user2.id).exists())
        self.assertFalse(pulse.liked_by.filter(id=user2.id).exists())

    def test_disliked_pulse_becoming_liked_removes_dislike(self):
        user1 = CreateTestUserHelper.create_test_user()
        user2 = CreateTestUserHelper.create_test_user()
        pulse = CreateTestUserGeneratedContentHelper.create_test_pulse(creator=user1)

        pulse.disliked_by.add(user2)

        self.assertTrue(pulse.disliked_by.filter(id=user2.id).exists())
        self.assertFalse(pulse.liked_by.filter(id=user2.id).exists())

        pulse.liked_by.add(user2)

        self.assertTrue(pulse.liked_by.filter(id=user2.id).exists())
        self.assertFalse(pulse.disliked_by.filter(id=user2.id).exists())

    def test_liked_reply_becoming_disliked_removes_like(self):
        user1 = CreateTestUserHelper.create_test_user()
        user2 = CreateTestUserHelper.create_test_user()
        reply = CreateTestUserGeneratedContentHelper.create_test_reply(creator=user1)

        reply.liked_by.add(user2)

        self.assertTrue(reply.liked_by.filter(id=user2.id).exists())
        self.assertFalse(reply.disliked_by.filter(id=user2.id).exists())

        reply.disliked_by.add(user2)

        self.assertTrue(reply.disliked_by.filter(id=user2.id).exists())
        self.assertFalse(reply.liked_by.filter(id=user2.id).exists())

    def test_disliked_reply_becoming_liked_removes_dislike(self):
        user1 = CreateTestUserHelper.create_test_user()
        user2 = CreateTestUserHelper.create_test_user()
        reply = CreateTestUserGeneratedContentHelper.create_test_reply(creator=user1)

        reply.disliked_by.add(user2)

        self.assertTrue(reply.disliked_by.filter(id=user2.id).exists())
        self.assertFalse(reply.liked_by.filter(id=user2.id).exists())

        reply.liked_by.add(user2)

        self.assertTrue(reply.liked_by.filter(id=user2.id).exists())
        self.assertFalse(reply.disliked_by.filter(id=user2.id).exists())
