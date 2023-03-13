"""
    Validators in pulsifi app.
"""

import re as regex
from typing import Collection

import tldextract
from confusable_homoglyphs import confusables
from django.contrib import auth
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, RegexValidator
from django.utils import deconstruct

get_user_model = auth.get_user_model  # NOTE: Adding external package functions to the global scope for frequent usage
deconstructible = deconstruct.deconstructible


@deconstructible
class ReservedNameValidator:
    """ Validator which disallows many reserved names as field values. """

    # noinspection SpellCheckingInspection
    DEFAULT_SPECIAL_HOSTNAMES = {
        "autoconfig",
        "autodiscover",
        "broadcasthost",
        "isatap",
        "localdomain",
        "localhost",
        "wpad"
    }
    """Hostnames with special/reserved meaning."""

    # noinspection SpellCheckingInspection
    DEFAULT_PROTOCOL_HOSTNAMES = {
        "css",
        "ftp",
        "html",
        "http",
        "https",
        "https",
        "imap",
        "ip",
        "iscsi",
        "js",
        "mail",
        "news",
        "ntp",
        "pop",
        "pop3",
        "smtp",
        "tcp",
        "udp",
        "usenet",
        "uucp",
        "webmail",
        "www"
    }
    """ Common protocol hostnames. """

    # noinspection SpellCheckingInspection
    DEFAULT_CA_ADDRESSES = {
        "admin",
        "administrator",
        "hostmaster",
        "info",
        "is",
        "it",
        "mis",
        "postmaster",
        "root",
        "ssladmin",
        "ssladministrator",
        "sslwebmaster",
        "sysadmin",
        "webmaster"
    }
    """
        Email addresses known used by certificate authorities during
        verification.
    """

    DEFAULT_RFC_2142 = {
        "abuse",
        "marketing",
        "noc",
        "sales",
        "security",
        "support"
    }
    """ RFC-2142-defined names not already covered. """

    DEFAULT_NOREPLY_ADDRESSES = {
        "mailer-daemon",
        "nobody",
        "noreply",
        "no-reply"
    }
    """ Common no-reply email addresses. """

    # noinspection SpellCheckingInspection
    DEFAULT_SENSITIVE_FILENAMES = {
        "clientaccesspolicy.xml",
        "crossdomain.xml",
        "favicon.ico",
        "humans.txt",
        "keybase.txt",
        "robots.txt",
        ".htaccess",
        ".htpasswd"
    }
    """ Sensitive filenames. """

    # noinspection SpellCheckingInspection
    DEFAULT_OTHER_SENSITIVE_NAMES = {
        "account",
        "accounts",
        "auth",
        "authorize",
        "blog",
        "buy",
        "cart",
        "clients",
        "config",
        "contact",
        "contactus",
        "contact-us",
        "copyright",
        "dashboard",
        "doc",
        "docs",
        "download",
        "downloads",
        "enquiry",
        "faq",
        "help",
        "inquiry",
        "information",
        "license",
        "login",
        "logout",
        "me",
        "myaccount",
        "moderator",
        "oauth",
        "pay",
        "payment",
        "payments",
        "plans",
        "portfolio",
        "preferences",
        "price"
        "pricing",
        "privacy",
        "profile",
        "puls",
        "register",
        "reply",
        "report",
        "secure",
        "settings",
        "shop",
        "shopping",
        "signin",
        "signup",
        "ssl",
        "status",
        "store",
        "subscribe",
        "terms",
        "test",
        "tos",
        "user",
        "users",
        "weblog",
        "work"
    }
    """
        Other names which could be problems depending on URL/subdomain
        structure.
    """

    def __init__(self, reserved_names: Collection[str] = None) -> None:
        if reserved_names is None:
            reserved_names: set[str] = self.DEFAULT_SPECIAL_HOSTNAMES | self.DEFAULT_PROTOCOL_HOSTNAMES | self.DEFAULT_CA_ADDRESSES | self.DEFAULT_RFC_2142 | self.DEFAULT_NOREPLY_ADDRESSES | self.DEFAULT_SENSITIVE_FILENAMES | self.DEFAULT_OTHER_SENSITIVE_NAMES
        else:
            reserved_names = set(reserved_names)
        self.reserved_names = reserved_names

    def __call__(self, value: str) -> None:
        if not isinstance(value, str):
            return

        if value in self.reserved_names or value.startswith(".well-known"):
            raise ValidationError("This name is reserved and cannot be registered.", code="invalid")

    def __eq__(self, other) -> bool:
        return self.reserved_names == other.reserved_names


@deconstructible
class HTML5EmailValidator(RegexValidator):
    """ Validator which applies HTML5's email address rules. """

    HTML5_EMAIL_RE = (
        r"^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]"
        r"+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}"
        r"[a-zA-Z0-9])?(?:\.[a-zA-Z0-9]"
        r"(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
    )  # SOURCE: WHATWG HTML5 spec, section 4.10.5.1.5.

    message = EmailValidator.message
    regex = regex.compile(HTML5_EMAIL_RE)


@deconstructible
class FreeEmailValidator:
    """
        Validator which disallows common temporary/free email hosting services
        as email address domain values.
    """

    # noinspection SpellCheckingInspection
    DEFAULT_FREE_EMAIL_DOMAINS = {
        "decabg.eu",
        "gufum.com",
        "tmail9.com",
        "ema-sofia.eu",
        "dropsin.net",
        "finews.biz",
        "triots.com",
        "rungel.net",
        "jollyfree.com",
        "gotgel.org",
        "prolug.com",
        "tmail1.com",
        "tmail.com",
        "tempmail.com",
        "tmail2.com",
        "tmail3.com",
        "tmail4.com",
        "tmail5.com",
        "tmail6.com",
        "tmail7.com",
        "tmail8.com",
        "tmail9.com",
        "lyricspad.net",
        "lyft.live",
        "dewareff.com",
        "kaftee.com",
        "letpays.com"
    }

    def __init__(self, free_email_domains: Collection[str] = None) -> None:
        if free_email_domains is None:
            free_email_domains: set[str] = self.DEFAULT_FREE_EMAIL_DOMAINS
        else:
            free_email_domains = set(free_email_domains)

        self.free_email_domains = free_email_domains

    def __call__(self, value: str) -> None:
        if not isinstance(value, str):
            return

        if value.count("@") != 1:
            return

        if value.rpartition("@")[2] in self.free_email_domains:
            raise ValidationError("Registration using free email addresses is prohibited. Please supply a different email address.", code="invalid")

    def __eq__(self, other) -> bool:
        return self.free_email_domains == other.free_email_domains


@deconstructible
class ExampleEmailValidator:
    """ Validator which disallows common example address domain values. """

    DEFAULT_EXAMPLE_EMAIL_DOMAINS = {"example", "test"}

    def __init__(self, example_email_domains: Collection[str] = None) -> None:
        if example_email_domains is None:
            example_email_domains: set[str] = self.DEFAULT_EXAMPLE_EMAIL_DOMAINS
        else:
            example_email_domains = set(example_email_domains)

        self.example_email_domains = example_email_domains

    def __call__(self, value: str) -> None:
        if not isinstance(value, str):
            return

        if value.count("@") != 1:
            return

        if tldextract.extract(value.rpartition("@")[2]).domain in self.example_email_domains:
            raise ValidationError("Registration using unresolvable example email addresses is prohibited. Please supply a different email address.", code="invalid")


@deconstructible
class PreexistingEmailTLDValidator:
    """
        Validator which disallows email address values (without any subdomain
        parts) that are already used by another user (even if it is not that
        other user's primary email address).
    """

    def __call__(self, value: str) -> None:
        if not isinstance(value, str):
            return

        if value.count("@") != 1:
            return

        local: str
        seperator: str
        domain: str
        local, seperator, domain = value.rpartition("@")

        if get_user_model().objects.exclude(email=value).filter(email__icontains=seperator.join((local, tldextract.extract(domain).domain))).exists():
            raise ValidationError(f"The Email Address: {value} is already in use by another user.", code="unique")


@deconstructible
class ConfusableStringValidator:
    """
        Validator which disallows 'dangerous' strings likely to represent
        homograph attacks. A string is 'dangerous' if it is mixed-script (as
        defined by Unicode 'Script' property) and contains one or more
        characters appearing in the Unicode Visually Confusable Characters
        file.
    """

    def __call__(self, value: str) -> None:
        if not isinstance(value, str):
            return

        if confusables.is_dangerous(value):
            raise ValidationError("This name cannot be registered. Please choose a different name.", code="invalid")


@deconstructible
class ConfusableEmailValidator:
    """
        Validator which disallows 'dangerous' email addresses likely to
        represent homograph attacks. An email address is 'dangerous' if either
        the local-part or the domain, considered on their own, are mixed-script
        and contain one or more characters appearing in the Unicode Visually
        Confusable Characters file.
    """

    def __call__(self, value: str) -> None:
        if not isinstance(value, str):
            return

        if value.count("@") != 1:
            return

        local: str
        domain: str
        local, _, domain = value.rpartition("@")

        if confusables.is_dangerous(local) or confusables.is_dangerous(domain):
            raise ValidationError("This email address cannot be registered. Please supply a different email address.", code="invalid")
