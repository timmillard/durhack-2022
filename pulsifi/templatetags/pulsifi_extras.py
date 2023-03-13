"""
    Extra Tags & Filters available for use in the templating engine within the
    pulsifi app.
"""

from re import Match as RegexMatch, sub as regex_sub

from django import template
from django.contrib import auth
from django.db import models
from django.template import defaultfilters, loader as template_utils
from django.utils import html as html_utils, safestring

get_user_model = auth.get_user_model  # NOTE: Adding external package functions to the global scope for frequent usage

register = template.Library()


# noinspection SpellCheckingInspection
@register.filter(needs_autoescape=True)
@defaultfilters.stringfilter
def format_mentions(value: str, autoescape=True) -> safestring.SafeString:
    """
        Formats the given string value, with any mentions of a user
        (E.g. @pulsifi) turned into the rendered HTML template of linking to
        that user (E.g. <a href="/user/@pulsifi">@pulsifi</a>)
    """

    if autoescape:
        esc_func = html_utils.conditional_escape
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

        return template_utils.render_to_string("pulsifi/mention_user_snippet.html", {"mentioned_user": mentioned_user}).strip()

    return safestring.mark_safe(
        regex_sub(
            r"@(?P<mention>[\w.-]+)",
            is_valid,
            esc_func(value)
        )
    )


@register.filter()
def classname(value):
    try:
        if isinstance(value, models.Model) or issubclass(value, models.Model):
            return value._meta.model_name
    except TypeError:
        pass
    return str(type(value)).title()


# noinspection SpellCheckingInspection
@register.filter()
def verbosename(value, plural=False):
    try:
        if isinstance(value, models.Model) or issubclass(value, models.Model):
            if plural:
                return value._meta.verbose_name_plural
            else:
                return value._meta.verbose_name
    except TypeError:
        pass
    return str(type(value)).title()
