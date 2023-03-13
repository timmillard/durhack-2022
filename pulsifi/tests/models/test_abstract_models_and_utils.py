"""
    Automated test suite for abstract models in pulsifi app.
"""

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import Group

from pulsifi.exceptions import ReportableContentTypeNamesSettingError
from pulsifi.models import utils as pulsifi_models_utils
from pulsifi.tests.utils import Base_TestCase, CreateTestUserGeneratedContentHelper, CreateTestUserHelper

get_user_model = auth.get_user_model  # NOTE: Adding external package functions to the global scope for frequent usage


class get_random_moderator_id_Util_Function_Tests(Base_TestCase):
    """
        Tests for correct execution of the get_random_moderator_id() util function.
    """

    def test_get_random_moderator_id_with_no_reportable_objects_and_no_moderators(self):
        """
            Validates that None is returned when get_random_moderator_id() is
            called and no moderators exist and no reportable objects exist.
            This prevents crashing during initialisation, as this function is
            parsed before reportable objects have been loaded (which would
            normally cause a crash).
        """

        self.assertIsNone(pulsifi_models_utils.get_random_moderator_id())

    def test_get_random_moderator_id_with_reportable_objects_and_no_moderators(self):
        """
            Validates that calling get_random_moderator_id() raises
            User.DoesNotExist when reportable objects do exist, but no
            moderators exist, so no moderator ID can be returned.
        """

        for model_name in settings.REPORTABLE_CONTENT_TYPE_NAMES:
            if model_name in CreateTestUserGeneratedContentHelper.GENERATABLE_OBJECTS:
                CreateTestUserGeneratedContentHelper.create_test_user_generated_content(model_name)

            elif model_name in CreateTestUserHelper.GENERATABLE_OBJECTS:
                CreateTestUserHelper.create_test_user()

            else:
                raise ReportableContentTypeNamesSettingError("No test data creation helper available for the given reportable_content_type_name", reportable_content_type_name=model_name)

            with self.assertRaises(get_user_model().DoesNotExist):
                pulsifi_models_utils.get_random_moderator_id()

    def test_get_random_moderator_id_with_reportable_objects_and_moderators(self):
        """
            Validates that get_random_moderator_id() returns the single valid
            moderator's ID when reportable objects exist and a moderator
            exists.
        """

        user = CreateTestUserHelper.create_test_user()
        user.groups.add(Group.objects.get(name="Moderators"))

        self.assertEqual(
            user.id,
            pulsifi_models_utils.get_random_moderator_id()
        )


class Custom_Base_Model_Tests(Base_TestCase):
    pass
