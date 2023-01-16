"""
    Automated test suite for concrete models in pulsifi app.
"""
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db.models import BooleanField
from django.test import TestCase

from pulsifi.models import Report
from pulsifi.tests.utils import CreateTestUserGeneratedContentHelper, CreateTestUserHelper, GetFieldsHelper


# TODO: tests docstrings


class User_Model_Tests(TestCase):
    def test_refresh_from_database_updates_non_relation_fields(self):  # TODO: test validators & validation errors from clean method
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

        self.assertTrue(user.visible)
        self.assertTrue(user.is_active)

        user.visible = False

        self.assertFalse(user.visible)
        self.assertFalse(user.is_active)

    def test_stringify_displays_in_correct_format(self):
        user = CreateTestUserHelper.create_test_user()

        self.assertEqual(str(user), f"@{user.username}")

        user.update(is_active=False)

        self.assertEqual(
            str(user),
            "".join(letter + "\u0336" for letter in f"@{user.username}")
        )

    def test_super_user_added_to_admin_group(self):
        user = CreateTestUserHelper.create_test_user()
        admin_group = Group.objects.create(name="Admins")

        self.assertNotIn(admin_group, user.groups.all())

        user.update(is_superuser=True)

        self.assertIn(admin_group, user.groups.all())

    def test_super_user_made_staff(self):
        user = CreateTestUserHelper.create_test_user()

        self.assertFalse(user.is_staff)

        user.update(is_superuser=True)

        self.assertTrue(user.is_staff)

    def test_user_added_to_moderators_group_made_staff(self):
        user = CreateTestUserHelper.create_test_user()
        moderator_group = Group.objects.create(name="Moderators")

        self.assertFalse(user.is_staff)

        user.groups.add(moderator_group)

        user.refresh_from_db()

        self.assertTrue(user.is_staff)

    def test_moderators_group_has_user_added_made_staff(self):
        user = CreateTestUserHelper.create_test_user()
        moderator_group = Group.objects.create(name="Moderators")

        self.assertFalse(user.is_staff)

        moderator_group.user_set.add(user)

        user.refresh_from_db()

        self.assertTrue(user.is_staff)

    def test_dots_removed_from_local_part_of_email(self):
        local_email = "test.local.email"
        domain_email = "test.domain.email.com"
        user = CreateTestUserHelper.create_test_user(email="@".join([local_email, domain_email]))

        self.assertEqual(user.email, "@".join([local_email.replace(".", ""), domain_email]))

    def test_plus_alias_removed_from_local_part_of_email(self):
        local_email = "test+local+email"
        domain_email = "test.domain.email.com"
        user = CreateTestUserHelper.create_test_user(email="@".join([local_email, domain_email]))

        self.assertEqual(user.email, "@".join([local_email.split("+", maxsplit=1)[0], domain_email]))

    def test_google_email_alias_replaced(self):
        local_email = "test"
        domain_email = "googlemail.com"
        user = CreateTestUserHelper.create_test_user(email="@".join([local_email, domain_email]))

        self.assertEqual(user.email, "@".join([local_email, "gmail.com"]))

    def test_email_address_object_from_user_primary_email(self):
        user = CreateTestUserHelper.create_test_user()

        self.assertFalse(EmailAddress.objects.filter(user=user, email=user.email).exists())

        user.save()

        self.assertTrue(EmailAddress.objects.filter(user=user, email=user.email).exists())

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


class _User_Generated_Content_Model_Tests(TestCase):  # TODO: test validation errors from clean method
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


class Report_Model_Tests(TestCase):
    def test_assigned_staff_is_not_reported_object(self):
        user1 = CreateTestUserHelper.create_test_user()
        user2 = CreateTestUserHelper.create_test_user()
        moderator_group = Group.objects.create(name="Moderators")
        user2.groups.add(moderator_group)

        with self.assertRaises(ValidationError) as e:
            Report.objects.create(
                reporter=user1,
                _content_type=ContentType.objects.get_for_model(type(user2)),
                _object_id=user2.id,
                reason="test reason message",
                category=Report.SPAM
            )
        self.assertEqual(list(e.exception.error_dict.keys())[0], "_object_id")

    def test_pulse_created_by_admin_cannot_be_reported(self):
        user1 = CreateTestUserHelper.create_test_user()
        user2 = CreateTestUserHelper.create_test_user(is_superuser=True)
        user3 = CreateTestUserHelper.create_test_user()
        admin_group = Group.objects.create(name="Admins")
        moderator_group = Group.objects.create(name="Moderators")
        user2.groups.add(admin_group)
        user3.groups.add(moderator_group)
        pulse = CreateTestUserGeneratedContentHelper.create_test_pulse(creator=user2)

        with self.assertRaises(ValidationError) as e:
            Report.objects.create(
                reporter=user1,
                _content_type=ContentType.objects.get_for_model(type(pulse)),
                _object_id=pulse.id,
                reason="test reason message",
                category=Report.SPAM
            )
        self.assertEqual(list(e.exception.error_dict.keys())[0], "_object_id")

    def test_reply_created_by_admin_cannot_be_reported(self):
        user1 = CreateTestUserHelper.create_test_user()
        user2 = CreateTestUserHelper.create_test_user(is_superuser=True)
        user3 = CreateTestUserHelper.create_test_user()
        admin_group = Group.objects.create(name="Admins")
        moderator_group = Group.objects.create(name="Moderators")
        user2.groups.add(admin_group)
        user3.groups.add(moderator_group)
        reply = CreateTestUserGeneratedContentHelper.create_test_reply(creator=user2)

        with self.assertRaises(ValidationError) as e:
            Report.objects.create(
                reporter=user1,
                _content_type=ContentType.objects.get_for_model(type(reply)),
                _object_id=reply.id,
                reason="test reason message",
                category=Report.SPAM
            )
        self.assertEqual(list(e.exception.error_dict.keys())[0], "_object_id")
