"""
    Extra Tags & Filters available for use in the templating engine within the
    pulsifi app.
"""

from re import Match as RegexMatch, sub as regex_sub

from django import template
from django.contrib.auth import get_user_model
from django.template.defaultfilters import stringfilter
from django.template.loader import render_to_string
from django.utils.html import conditional_escape
from django.utils.safestring import SafeString, mark_safe

register = template.Library()


# noinspection SpellCheckingInspection
@register.filter(needs_autoescape=True)
@stringfilter
def format_mentions(value: str, autoescape=True) -> SafeString:
    """
        Formats the given string value, with any mentions of a user
        (E.g. @pulsifi) turned into the rendered HTML template of linking to
        that user (E.g. <a href="/user/@pulsifi">@pulsifi</a>)
    """

    if autoescape:
        esc_func = conditional_escape
    else:
        # noinspection PyMissingOrEmptyDocstring
        def esc_func(x: str) -> str:
            return x

    def is_valid(possible_mention: RegexMatch) -> str:
        """
            Returns the HTML formatted mention if the regex match was a valid
            user, otherwise returns the original text.
        """

        possible_mention: str = possible_mention.group("mention")

        try:
            mentioned_user = get_user_model().objects.get(username=possible_mention)
        except get_user_model().DoesNotExist:
            return f"@{possible_mention}"

        return render_to_string("pulsifi/mention_user_snippet.html", {"mentioned_user": mentioned_user}).strip()

    return mark_safe(
        regex_sub(
            r"@(?P<mention>[\w.-]+)",
            is_valid,
            esc_func(value)
        )
    )
