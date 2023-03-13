"""
    Automated test suite for extra template tags & filters in pulsifi app.
"""

from pulsifi.templatetags import pulsifi_extras
from pulsifi.tests.utils import Base_TestCase, CreateTestUserHelper


class Extra_Filters_Tests(Base_TestCase):
    def test_format_mentions_filter_user_exists(self):
        CreateTestUserHelper.create_test_user(username="pulsifi", is_staff=True)
        # noinspection SpellCheckingInspection
        CreateTestUserHelper.create_test_user(username="otheruser")

        self.assertEqual(
            "This is a test for <a href=\"/user/@pulsifi/\">@pulsifi</a>!! and other text!",
            pulsifi_extras.format_mentions("This is a test for @pulsifi!! and other text!")
        )

        # noinspection SpellCheckingInspection
        self.assertEqual(
            "This is a test for <a href=\"/user/@otheruser/\">@otheruser</a>!! and other text!",
            pulsifi_extras.format_mentions("This is a test for @otheruser!! and other text!")
        )

    def test_format_mentions_filter_user_not_exists(self):
        # noinspection SpellCheckingInspection
        self.assertEqual(
            "This is a test for @otheruser!! and other text!",
            pulsifi_extras.format_mentions("This is a test for @otheruser!! and other text!")
        )

    def test_format_mentions_filter_invalid_username(self):
        self.assertEqual(
            "This is a test for @$$hi and @admin and @https and @abuse and @docs!",
            pulsifi_extras.format_mentions("This is a test for @$$hi and @admin and @https and @abuse and @docs!")
        )
