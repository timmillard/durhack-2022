"""
    Automated test suite for concrete models in pulsifi app.
"""
from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db.models import BooleanField

from pulsifi.models import Report, User
from pulsifi.tests.utils import Base_TestCase, CreateTestUserGeneratedContentHelper, CreateTestUserHelper, GetFieldsHelper


# TODO: tests docstrings


class User_Model_Tests(Base_TestCase):
    def test_refresh_from_database_updates_non_relation_fields(self):  # TODO: test validators & validation errors from clean method
        user = CreateTestUserHelper.create_test_user()
        old_user: User = get_user_model().objects.get(id=user.id)

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

    def test_visible_shortcut_in_memory(self):
        user = CreateTestUserHelper.create_test_user()

        self.assertTrue(user.visible)
        self.assertTrue(user.is_active)

        user.visible = False

        self.assertFalse(user.visible)
        self.assertFalse(user.is_active)

    def test_visible_shortcut_in_database(self):
        user = CreateTestUserHelper.create_test_user()

        self.assertTrue(user.visible)
        self.assertTrue(user.is_active)

        user.update(visible=False)

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

    def test_user_becomes_superuser_put_in_admin_group(self):
        user = CreateTestUserHelper.create_test_user()
        admin_group = Group.objects.get(name="Admins")

        self.assertNotIn(admin_group, user.groups.all())

        user.update(is_superuser=True)

        self.assertIn(admin_group, user.groups.all())

    def test_superuser_has_groups_changed_kept_in_admin_group(self):
        user = CreateTestUserHelper.create_test_user(is_superuser=True)
        admin_group = Group.objects.get(name="Admins")

        self.assertIn(admin_group, user.groups.all())

        user.groups.remove(admin_group)

        self.assertIn(admin_group, user.groups.all())

        user.groups.set(Group.objects.none())

        self.assertIn(admin_group, user.groups.all())

        user.groups.set([])

        self.assertIn(admin_group, user.groups.all())

        user.groups.clear()

        self.assertIn(admin_group, user.groups.all())

    def test_admin_group_has_users_changed_superusers_kept_in_admin_group(self):
        user = CreateTestUserHelper.create_test_user(is_superuser=True)
        admin_group = Group.objects.get(name="Admins")

        self.assertIn(user, admin_group.user_set.all())

        admin_group.user_set.remove(user)

        self.assertIn(user, admin_group.user_set.all())

        admin_group.user_set.set(get_user_model().objects.none())

        self.assertIn(user, admin_group.user_set.all())

        admin_group.user_set.set([])

        self.assertIn(user, admin_group.user_set.all())

        admin_group.user_set.clear()

        self.assertIn(user, admin_group.user_set.all())

    def test_super_user_made_staff(self):
        user = CreateTestUserHelper.create_test_user()

        self.assertFalse(user.is_staff)

        user.update(is_superuser=True)

        self.assertTrue(user.is_staff)

    def test_user_added_to_staff_group_made_staff(self):
        staff_group_name: str
        for staff_group_name in get_user_model().STAFF_GROUP_NAMES:
            user = CreateTestUserHelper.create_test_user()
            group = Group.objects.get(name=staff_group_name)

            self.assertFalse(user.is_staff)

            user.groups.add(group)

            user.refresh_from_db()

            self.assertTrue(user.is_staff)

    def test_moderator_group_has_user_added_made_staff(self):
        staff_group_name: str
        for staff_group_name in get_user_model().STAFF_GROUP_NAMES:
            user = CreateTestUserHelper.create_test_user()
            group = Group.objects.get(name=staff_group_name)

            self.assertFalse(user.is_staff)

            group.user_set.add(user)

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

    def test_reverse_liked_content_becoming_disliked_removes_like(self):
        user1 = CreateTestUserHelper.create_test_user()
        user2 = CreateTestUserHelper.create_test_user()
        for model in ["pulse", "reply"]:
            content = CreateTestUserGeneratedContentHelper.create_test_user_generated_content(model, creator=user1)

            if model == "pulse":
                user2.liked_pulse_set.add(content)
            elif model == "reply":
                user2.liked_reply_set.add(content)

            self.assertTrue(content.liked_by.filter(id=user2.id).exists())
            self.assertFalse(content.disliked_by.filter(id=user2.id).exists())

            if model == "pulse":
                user2.disliked_pulse_set.add(content)
            elif model == "reply":
                user2.disliked_reply_set.add(content)

            self.assertTrue(content.disliked_by.filter(id=user2.id).exists())
            self.assertFalse(content.liked_by.filter(id=user2.id).exists())

    def test_reverse_disliked_content_becoming_liked_removes_dislike(self):
        user1 = CreateTestUserHelper.create_test_user()
        user2 = CreateTestUserHelper.create_test_user()
        for model in ["pulse", "reply"]:
            content = CreateTestUserGeneratedContentHelper.create_test_user_generated_content(model, creator=user1)

            if model == "pulse":
                user2.disliked_pulse_set.add(content)
            elif model == "reply":
                user2.disliked_reply_set.add(content)

            self.assertTrue(content.disliked_by.filter(id=user2.id).exists())
            self.assertFalse(content.liked_by.filter(id=user2.id).exists())

            if model == "pulse":
                user2.liked_pulse_set.add(content)
            elif model == "reply":
                user2.liked_reply_set.add(content)

            self.assertTrue(content.liked_by.filter(id=user2.id).exists())
            self.assertFalse(content.disliked_by.filter(id=user2.id).exists())


class _User_Generated_Content_Model_Tests(Base_TestCase):  # TODO: test validation errors from clean method
    def test_liked_content_becoming_disliked_removes_like(self):
        user1 = CreateTestUserHelper.create_test_user()
        user2 = CreateTestUserHelper.create_test_user()
        for model in ["pulse", "reply"]:
            content = CreateTestUserGeneratedContentHelper.create_test_user_generated_content(model, creator=user1)

            content.liked_by.add(user2)

            self.assertTrue(content.liked_by.filter(id=user2.id).exists())
            self.assertFalse(content.disliked_by.filter(id=user2.id).exists())

            content.disliked_by.add(user2)

            self.assertTrue(content.disliked_by.filter(id=user2.id).exists())
            self.assertFalse(content.liked_by.filter(id=user2.id).exists())

    def test_disliked_content_becoming_liked_removes_dislike(self):
        user1 = CreateTestUserHelper.create_test_user()
        user2 = CreateTestUserHelper.create_test_user()
        for model in ["pulse", "reply"]:
            content = CreateTestUserGeneratedContentHelper.create_test_user_generated_content(model, creator=user1)

            content.disliked_by.add(user2)

            self.assertTrue(content.disliked_by.filter(id=user2.id).exists())
            self.assertFalse(content.liked_by.filter(id=user2.id).exists())

            content.liked_by.add(user2)

            self.assertTrue(content.liked_by.filter(id=user2.id).exists())
            self.assertFalse(content.disliked_by.filter(id=user2.id).exists())

    def test_stringify_displays_in_correct_format(self):
        for model in ["pulse", "reply"]:
            content = CreateTestUserGeneratedContentHelper.create_test_user_generated_content(model)

            if model == "pulse":
                self.assertEqual(
                    str(content),
                    f"{content.creator}, {content.message[:settings.MESSAGE_DISPLAY_LENGTH]}"
                )
            if model == "reply":
                self.assertEqual(
                    str(content),
                    f"{content.creator}, {content.message[:settings.MESSAGE_DISPLAY_LENGTH]} (For object - {type(content.replied_content).__name__.upper()[0]} | {content.replied_content})"[:100]
                )

            content.update(visible=False)

            if model == "pulse":
                self.assertEqual(
                    str(content),
                    f"{content.creator}, " + "".join(letter + "\u0336" for letter in content.message[:settings.MESSAGE_DISPLAY_LENGTH])
                )
            if model == "reply":
                self.assertEqual(
                    str(content),
                    (f"{content.creator}, " + "".join(letter + "\u0336" for letter in content.message[:settings.MESSAGE_DISPLAY_LENGTH]) + f" (For object - {type(content.replied_content).__name__.upper()[0]} | {content.replied_content})")[:100]
                )


class Report_Model_Tests(Base_TestCase):
    def test_assigned_staff_is_not_reported_object(self):
        user1 = CreateTestUserHelper.create_test_user()
        user2 = CreateTestUserHelper.create_test_user()
        user2.groups.add(Group.objects.get(name="Moderators"))

        with self.assertRaises(ValidationError) as e:
            Report.objects.create(
                reporter=user1,
                _content_type=ContentType.objects.get_for_model(type(user2)),
                _object_id=user2.id,
                reason="test reason message",
                category=Report.SPAM
            )
        self.assertEqual(list(e.exception.error_dict.keys())[0], "_object_id")

    def test_content_created_by_admin_cannot_be_reported(self):
        user1 = CreateTestUserHelper.create_test_user()
        user2 = CreateTestUserHelper.create_test_user()
        user3 = CreateTestUserHelper.create_test_user()
        user2.groups.add(Group.objects.get(name="Admins"))
        user3.groups.add(Group.objects.get(name="Moderators"))
        for model in ["pulse", "reply"]:
            content = CreateTestUserGeneratedContentHelper.create_test_user_generated_content(model, creator=user2)

            with self.assertRaises(ValidationError) as e:
                Report.objects.create(
                    reporter=user1,
                    _content_type=ContentType.objects.get_for_model(type(content)),
                    _object_id=content.id,
                    reason="test reason message",
                    category=Report.SPAM
                )
            self.assertEqual(list(e.exception.error_dict.keys())[0], "_object_id")

    def test_reported_user_is_not_the_only_moderator(self):
        user1 = CreateTestUserHelper.create_test_user()
        user2 = CreateTestUserHelper.create_test_user()
        user2.groups.add(Group.objects.get(name="Moderators"))

        with self.assertRaises(ValidationError) as e:
            Report.objects.create(
                reporter=user1,
                _content_type=ContentType.objects.get_for_model(get_user_model()),
                _object_id=user2.id,
                reason="test reason message",
                category=Report.SPAM
            )
        self.assertEqual(list(e.exception.error_dict.keys())[0], "_object_id")

    def test_reporter_is_not_the_only_moderator(self):
        user1 = CreateTestUserHelper.create_test_user()
        user2 = CreateTestUserHelper.create_test_user()
        user2.groups.add(Group.objects.get(name="Moderators"))
        for model in ["pulse", "reply"]:
            content = CreateTestUserGeneratedContentHelper.create_test_user_generated_content(model, creator=user1)

            with self.assertRaises(ValidationError) as e:
                Report.objects.create(
                    reporter=user2,
                    _content_type=ContentType.objects.get_for_model(type(content)),
                    _object_id=content.id,
                    reason="test reason message",
                    category=Report.SPAM
                )
            self.assertEqual(list(e.exception.error_dict.keys())[0], "reporter")
