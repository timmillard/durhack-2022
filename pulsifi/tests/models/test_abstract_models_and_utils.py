"""
    Automated test suite for abstract models in pulsifi app.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from pulsifi.models import get_random_staff_member_id
from pulsifi.tests.utils import Base_TestCase, CreateTestUserGeneratedContentHelper, CreateTestUserHelper


# TODO: tests docstrings

class Get_Random_Staff_Member_Util_Function_Tests(Base_TestCase):
    def test_get_random_staff_member_with_no_reportable_objects_and_no_staff_members(self):
        self.assertIsNone(get_random_staff_member_id())

    def test_get_random_staff_member_with_reportable_objects_and_no_staff_members(self):
        for model in ["pulse", "reply", "user"]:
            if model in CreateTestUserGeneratedContentHelper.GENERATABLE_OBJECTS:
                reportable_object = CreateTestUserGeneratedContentHelper.create_test_user_generated_content(model)

            elif model in CreateTestUserHelper.GENERATABLE_OBJECTS:
                reportable_object = CreateTestUserHelper.create_test_user()

            # noinspection PyTypeChecker
            with self.assertRaises(get_user_model().DoesNotExist):
                get_random_staff_member_id()

    def test_get_random_staff_member_with_reportable_objects_and_staff_members(self):
        user = CreateTestUserHelper.create_test_user()
        user.groups.add(Group.objects.get(name="Moderators"))

        self.assertEqual(get_random_staff_member_id(), user.id)


class Custom_Base_Model_Tests(Base_TestCase):
    pass
