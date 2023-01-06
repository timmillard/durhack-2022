"""
    Automated test suite for abstract models in pulsifi app.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from pulsifi.models import get_random_staff_member
from pulsifi.tests.utils import CreateTestUserGeneratedContentHelper


# TODO: tests docstrings

class Get_Random_Staff_Member_Util_Function_Tests(TestCase):
    def test_get_random_staff_member_with_no_Replies(self):
        self.assertIsNone(get_random_staff_member())

    def test_get_random_staff_member_with_Replies_and_no_staff_members(self):
        CreateTestUserGeneratedContentHelper.create_test_reply()

        # noinspection PyTypeChecker
        with self.assertRaises(get_user_model().DoesNotExist):
            get_random_staff_member()

    def test_get_random_staff_member_with_Replies_and_staff_members(self):
        pass


class Custom_Base_Model_Tests(TestCase):
    pass


class Visible_Reportable_Model_Tests(TestCase):
    def test_string_when_visible(self):
        pass
