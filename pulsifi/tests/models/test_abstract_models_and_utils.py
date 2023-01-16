"""
    Automated test suite for abstract models in pulsifi app.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase

from pulsifi.models import get_random_staff_member
from pulsifi.tests.utils import CreateTestUserGeneratedContentHelper, CreateTestUserHelper


# TODO: tests docstrings

class Get_Random_Staff_Member_Util_Function_Tests(TestCase):
    def test_get_random_staff_member_with_no_reportable_objects_and_no_staff_members(self):
        self.assertIsNone(get_random_staff_member())

    def test_get_random_staff_member_with_reportable_objects_and_no_staff_members(self):
        CreateTestUserGeneratedContentHelper.create_test_reply()

        # noinspection PyTypeChecker
        with self.assertRaises(get_user_model().DoesNotExist):
            get_random_staff_member()

    def test_get_random_staff_member_with_reportable_objects_and_staff_members(self):
        Group.objects.create(name="Moderators")
        user = CreateTestUserHelper.create_test_user()
        user.groups.add(Group.objects.get(name="Moderators"))

        self.assertEqual(get_random_staff_member(), user.id)


class Custom_Base_Model_Tests(TestCase):
    pass


class Visible_Reportable_Model_Tests(TestCase):
    def test_string_when_visible(self):  # TODO: implement test_string_when_visible
        raise NotImplementedError
