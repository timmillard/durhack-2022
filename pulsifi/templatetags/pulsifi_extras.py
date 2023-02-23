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
    if autoescape:
        esc_func = conditional_escape
    else:
        def esc_func(x: str) -> str:
            return x

    def valid_mention(possible_mention: RegexMatch) -> str:

        possible_mention: str = possible_mention.group("mention")

        try:
            mentioned_user = get_user_model().objects.get(username=possible_mention)
        except get_user_model().DoesNotExist:
            return f"@{possible_mention}"

        return render_to_string("pulsifi/mention_user_snippet.html", {"mentioned_user": mentioned_user}).strip()

    result: str = regex_sub(r"@(?P<mention>[\w.-]+)", valid_mention, esc_func(value))
    return mark_safe(result)
